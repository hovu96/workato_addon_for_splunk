import sys, os, urllib2, time, json, ssl, base64, random
from splunklib import client, results as results_lib

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
while True:
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

def send_event_to_splunk(params):
    call_workato_addon("events","POST",params)
    time.sleep(2)

def run_splunk_search(query):
    job = s.search(query)
    while not job.is_done():
        time.sleep(.2)
    result_stream = job.results()
    results_reader = results_lib.ResultsReader(result_stream)
    events = []
    for result in results_reader:
        if isinstance(result, dict):
            events.append(result)
    return events

send_event_to_splunk({
    "payload": "test=1",
    })
results = run_splunk_search("search index=main earliest=-1m test=1")
if len(results)!=1:
    raise Exception("unexpected search result")
send_event_to_splunk({
    "payload": "test=2",
    "index": "test",
    "source": "test",
    "sourcetype": "test",
    "host": "test"
    })
results = run_splunk_search("search index=test earliest=-1m test=2 source=test sourcetype=test host=test")
if len(results)!=1:
    raise Exception("unexpected search result")

print "starting server  ..."
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
received_events = {}
just_received_request = False
class MyCallbackHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global just_received_request
        just_received_request = True
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        self.send_response(200)
        if self.path in received_events:
            alert = json.loads(post_body)
            received_events[self.path].append(alert)
        self.end_headers()
        self.wfile.write("")
server_address = ('', 80)
server = HTTPServer(server_address, MyCallbackHandler)
server.timeout = 1

def handle_server_requests():
    global just_received_request
    while True:
        just_received_request = False
        server.handle_request()
        if not just_received_request:
            break

def subscribe_alert(name):
    callback_path = "/%s_%s" % (name, random.random())
    received_events[callback_path] = []
    return call_workato_addon("alerts","POST",{
        "search_name": name,
        "callback_url": "http://%s%s" % (test_host, callback_path)
    }), callback_path

def unsubscribe_alert(name, payload, callback_path):
    del received_events[callback_path]
    return call_workato_addon("alerts","DELETE",payload)

print "subscribing realtime alert ..."
unsubscribe_data, subscription_key = subscribe_alert('realtime_alert')

print "Sending and waiting for events ..."
index = s.indexes['main']
while len(received_events[subscription_key])==0:
    with index.attached_socket(sourcetype='test') as sock:
        sock.send('Test event\\r\\n')
    handle_server_requests()

print "unsubscribing realtime alert ..."
unsubscribe_alert('realtime_alert', unsubscribe_data, subscription_key)

handle_server_requests()

print "checking service alerts status ..."
service_alert_name = 'IT Service Alerts'
service_alerts_search = s.saved_searches[service_alert_name]
if not service_alerts_search.disabled == "1":
    raise Exception("service alerts not disabled")
servicealerts_info = call_workato_addon("servicealerts","GET",None)
if servicealerts_info['disabled'] == "0":
    raise Exception("service alerts not disabled")
if not servicealerts_info['is_scheduled'] == "1":
    raise Exception("service alerts not scheduled")
if servicealerts_info['subscribed'] is True:
    raise Exception("somebody already subscribed for service alerts")

handle_server_requests()

def subscribe_service_alert():
    callback_path = "/servicealert_%s" % (random.random())
    received_events[callback_path] = []
    return call_workato_addon("servicealerts","POST",{
        "callback_url": "http://%s%s" % (test_host, callback_path)
    }), callback_path

def unsubscribe_service_alert(payload, callback_path):
    del received_events[callback_path]
    return call_workato_addon("servicealerts", "DELETE", payload)

print "subscribing service alert ..."
unsubscribe_data, subscription_key = subscribe_service_alert()

handle_server_requests()

print "checking service alerts status ..."
servicealerts_info = call_workato_addon("servicealerts","GET",None)
if servicealerts_info['disabled'] == "1":
    raise Exception("service alerts disabled")
if servicealerts_info['subscribed'] is False:
    raise Exception("somebody already subscribed for service alerts")

handle_server_requests()

print "creating service alert ..."
index = s.indexes['itsi_tracked_alerts']
with index.attached_socket(sourcetype='test') as sock:
    sock.send('event_id="event_id" severity="severity" title="title" severity_label="severity_label" description="description"\\r\\n')

handle_server_requests()

print "waiting for service alert ..."
while len(received_events[subscription_key])==0:
    server.handle_request()
service_alert = received_events[subscription_key][0]
#print service_alert

handle_server_requests()

print "unsubscribing service alert ..."
unsubscribe_service_alert(unsubscribe_data, subscription_key)

handle_server_requests()

print "checking service alerts status ..."
servicealerts_info = call_workato_addon("servicealerts","GET",None)
if servicealerts_info['disabled'] == "0":
    raise Exception("service alert enabled")
if servicealerts_info['subscribed'] is True:
    raise Exception("somebody already subscribed for service alerts")

handle_server_requests()

print "checking service alert status ..."
service_alerts_search = s.saved_searches[service_alert_name]
if not service_alerts_search.disabled:
    raise Exception("service alert enabled")

handle_server_requests()

callback_search_param = 'action.workato.param.callback_urls'

def iterate_callbacks(saved_search):
    if callback_search_param in saved_search.content:
        callbacks = saved_search[callback_search_param]
        for v in callbacks.split('|'):
            v=v.strip()
            if v:
                yield v

def get_callback_count(saved_search):
    cnt = 0
    for callback in iterate_callbacks(saved_search):
        cnt += 1
    return cnt

def has_callback_path(saved_search, callback_path):
    for callback in iterate_callbacks(saved_search):
        if callback.endswith(callback_path):
            return True
    return False

print "subscribing service alert (#1) ..."
unsubscribe_data_1, subscription_1_callback_path = subscribe_service_alert()

handle_server_requests()

print "checking service alert status ..."
service_alerts_search = s.saved_searches[service_alert_name]
if service_alerts_search.disabled == "1":
    raise Exception("service alert disabled")
if get_callback_count(service_alerts_search)!=1:
    raise Exception("unexpected callback count")
if not has_callback_path(service_alerts_search, subscription_1_callback_path):
    raise Exception("callback path missing")

handle_server_requests()

print "subscribing service alert (#2) ..."
unsubscribe_data_2, subscription_2_callback_path = subscribe_service_alert()

handle_server_requests()

print "checking service alert status ..."
service_alerts_search = s.saved_searches[service_alert_name]
if service_alerts_search.disabled == "1":
    raise Exception("service alert disabled")
if get_callback_count(service_alerts_search)!=2:
    raise Exception("unexpected callback count")
if not has_callback_path(service_alerts_search, subscription_1_callback_path):
    raise Exception("callback path missing")
if not has_callback_path(service_alerts_search, subscription_2_callback_path):
    raise Exception("callback path missing")

handle_server_requests()

print "creating service alert ..."
index = s.indexes['itsi_tracked_alerts']
with index.attached_socket(sourcetype='test') as sock:
    sock.send('event_id="2" severity="high" title="ein test" severity_label="unknown" description="description"\\r\\n')

handle_server_requests()

def has_service_alert(callback_path, event_id):
    for event in received_events[callback_path]:
        if event['event_id']==event_id:
            return True
    return False

print "waiting for service alerts ..."
while not has_service_alert(subscription_1_callback_path, "2"):
    server.handle_request()
while not has_service_alert(subscription_2_callback_path, "2"):
    server.handle_request()

handle_server_requests()

print "unsubscribing service alert (#2) ..."
unsubscribe_service_alert(unsubscribe_data_2, subscription_2_callback_path)

handle_server_requests()

print "checking service alert status ..."
service_alerts_search = s.saved_searches[service_alert_name]
if get_callback_count(service_alerts_search)!=1:
    raise Exception("unexpected callback count")
if service_alerts_search.disabled == "1":
    raise Exception("service alert enabled")
if not has_callback_path(service_alerts_search, subscription_1_callback_path):
    raise Exception("callback path missing")

handle_server_requests()

print "unsubscribing service alert (#1) ..."
unsubscribe_service_alert(unsubscribe_data_1, subscription_1_callback_path)

handle_server_requests()

print "checking service alert status ..."
service_alerts_search = s.saved_searches[service_alert_name]
if get_callback_count(service_alerts_search)!=0:
    raise Exception("unexpected callback count")
if service_alerts_search.disabled == "0":
    raise Exception("service alert enabled")

handle_server_requests()

def list_saved_search():
    return call_workato_addon("savedsearches","GET",None)

def run_saved_search(name):
    return call_workato_addon("savedsearches","POST",{
        "search_name": name
    })

print "getting saved searches ..."
saved_searches = list_saved_search()
if "latest_internal_event" not in saved_searches:
    raise Exception("missing search 'latest_internal_event'")

handle_server_requests()

print "running saved search ..."
results = run_saved_search("latest_internal_event")["results"]
if len(results)!=1:
    raise Exception("unexpected results: %s",results)

handle_server_requests()

print "done"
