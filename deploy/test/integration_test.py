import sys, os, urllib2, time, json, ssl, base64
import splunklib.client as client

splunk_host = sys.argv[1]
splunk_port = sys.argv[2]
test_host = sys.argv[3]

s = client.Service(
    username="admin",
    password="admin",
    port=splunk_port,
    scheme="https",
    host=splunk_host)

print "logging in ..."
e = None
remaining = 30
while remaining>0:
    time.sleep(1)
    try:
        s.login()
        e = None
        break
    except Exception, _e:
        e=_e
    remaining -= 1
if e:
    raise e

class Request(urllib2.Request):
    def set_method(self,method):
        self.__method=method
    def get_method(self):
        return self.__method

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def call_json_service(url, method, payload, authorization_header):
    if method=="GET":
        req = Request(url, headers={
            "Content-Type": "application/json",
            "Authorization": authorization_header,
        })
    else:
        req = Request(url, data=json.dumps(payload), headers={
            "Content-Type": "application/json",
            "Authorization": authorization_header,
        })
    req.set_method(method)
    res = urllib2.urlopen(req, context=ctx)
    if res.code!=200:
        raise Exception('response code %s' % res.code)
    body = res.read()
    return json.loads(body)

def call_workato_addon(name, method, payload):
    url = "https://%s:%s/services/workato/%s"%(splunk_host,splunk_port,name)
    auth = 'Basic %s' % base64.b64encode("admin:admin")
    return call_json_service(url, method, payload, auth)

print "checking version ..."
version = call_workato_addon("version","GET",None)
print "Splunk %s" % version["splunk_version"]
print "ITSI %s" % (version["itsi_version"] if version["itsi_version"] else "not installed")
print "ES %s" % (version["es_version"] if version["es_version"] else "not installed")
print "Add-on %s" % version["workato_version"]

print "getting scheduled searches ..."
searches = call_workato_addon("alerts","GET",None)
if "realtime_alert" not in searches:
    raise Exception("missing search 'realtime_alert'")

print "starting server  ..."
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
received_events={}
class MyCallbackHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        received_events['test'] = []
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write("Hello World !")
server_address = ('', 80)
server = HTTPServer(server_address, MyCallbackHandler)
server.timeout = 1

print "subscribing  ..."
unsubscribe_payload = call_workato_addon("alerts","POST",{
    "search_name": "realtime_alert",
    "callback_url": "http://%s/bla" % (test_host)
})

index = s.indexes['main']
while not "test" in received_events:
    print "sending new event ..."
    with index.attached_socket(sourcetype='test') as sock:
        sock.send('Test event\\r\\n')
    print "waiting for event ..."
    server.handle_request()

print "unsubscribing  ..."
call_workato_addon("alerts","DELETE",unsubscribe_payload)

print "done"
