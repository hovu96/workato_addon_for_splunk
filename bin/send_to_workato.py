import sys, os, datetime, json, urllib2
import splunklib.client as client
from splunklib.binding import _spliturl as spliturl
from splunklib.binding import namespace as namespace

def notify_subscribers(payload):

    server_uri = payload['server_uri']
    session_key = payload['session_key']
    configuration = payload['configuration']

    scheme, host, port, path = spliturl(server_uri)

    s = client.Service(
        token=session_key,
        port=port,
        scheme=scheme,
        host=host)

    subscriptions = s.confs['subscriptions']

    for subscription in subscriptions.iter():
        print >> sys.stderr, "INFO subscription %s" % subscription

    return

    #room = settings.get('field')
    body = json.dumps(dict(
        time = 123,
        host = "webserver1",
        source = "/var/log/messages",
        sourcetype = "access_combined"
    ))
    req = urllib2.Request("workato ...", body, {"Content-Type": "application/json"})
    res = urllib2.urlopen(req)
    body = res.read()
    print >> sys.stderr, "INFO server responded with HTTP status=%d" % res.code
    print >> sys.stderr, "DEBUG server response: %s" % json.dumps(body)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        payload = json.loads(sys.stdin.read())

        notify_subscribers(payload)
        print >> sys.stderr, "INFO Notifications sent out"
    else:
        print >> sys.stderr, "FATAL Unsupported execution mode (expected --execute flag)"
        sys.exit(1)
