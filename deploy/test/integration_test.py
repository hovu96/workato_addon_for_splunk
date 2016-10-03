import sys, os, urllib2, time, json, ssl, base64, random
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

while True:
    print "logging in ..."
    try:
        s.login()
        e = None
        break
    except:
        time.sleep(1)

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
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        self.send_response(200)
        #print "Received event on %s"%(self.path)
        received_events[self.path].append(post_body)
        self.end_headers()
        self.wfile.write("")
server_address = ('', 80)
server = HTTPServer(server_address, MyCallbackHandler)
server.timeout = 1

def subscribe_alert(name):
    callback_path = "/%s" % (random.random())
    received_events[callback_path] = []
    return call_workato_addon("alerts","POST",{
        "search_name": name,
        "callback_url": "http://%s%s" % (test_host, callback_path)
    }), callback_path

def unsubscribe_alert(name, payload):
    return call_workato_addon("alerts","DELETE",payload)

print "subscribing ..."
subscription, key = subscribe_alert('realtime_alert')

index = s.indexes['main']
while len(received_events[key])==0:
    print "sending new event ..."
    with index.attached_socket(sourcetype='test') as sock:
        sock.send('Test event\\r\\n')
    print "waiting for event ..."
    server.handle_request()

print "unsubscribing  ..."
unsubscribe_alert('realtime_alert',subscription)

#searches = call_workato_addon("servicealerts","GET",None)

print "done"
