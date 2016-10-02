import sys, os, urllib2, time, json, ssl, base64
import splunklib.client as client

splunk_host = sys.argv[1]
splunk_port = sys.argv[2]

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

print "done"

class Request(urllib2.Request):
    def set_method(self,method):
        self.__method=method
    def get_method(self):
        return self.__method

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def call_json_service(url, method, payload, authorization_header):
    req = Request(url, json.dumps(payload), {
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
    return call_json_service("https://%s:%s/services/workato/%s"%(splunk_host,splunk_port,name),"GET",None,'Basic %s' % base64.b64encode("admin:admin"))

version = call_workato_addon("version","GET",None)
print "Splunk %s" % version["splunk_version"]
print "ITSI %s" % (version["itsi_version"] if version["itsi_version"] else "not installed")
print "ES %s" % (version["es_version"] if version["es_version"] else "not installed")
print "Add-on %s" % version["workato_version"]

searches = call_workato_addon("scheduledsearches","GET",None)
print searches

#try:
#    line = sys.stdin.readline()
#except KeyboardInterrupt:
#    pass
