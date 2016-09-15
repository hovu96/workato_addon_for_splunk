import sys, os, datetime, json, urllib2
import splunklib.client as client
from splunklib.binding import _spliturl as spliturl
from splunklib.binding import namespace as namespace
import gzip, csv

def call_workato(payload):

    config = payload.get('configuration')

    callback_url = config.get('callback_url')
    print >> sys.stderr, "INFO callback_url=%s" % callback_url

    results_file = payload.get('results_file')

    with gzip.open(results_file, 'rb') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            payload = {}
            for name, value in row.iteritems():
                if not name.startswith('__mv'):
                    payload[name]=value
            print >> sys.stderr, "INFO sending %s ..." % payload
            req = urllib2.Request(callback_url, json.dumps(payload), {"Content-Type": "application/json"})
            res = urllib2.urlopen(req)
            body = res.read()
            print >> sys.stderr, "INFO server responded with HTTP status=%d" % res.code
            print >> sys.stderr, "DEBUG server response: %s" % json.dumps(body)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        payload = sys.stdin.read()
        print >> sys.stderr, "INFO " + payload
        payload = json.loads(payload)
        call_workato(payload)
        print >> sys.stderr, "INFO done"
    else:
        print >> sys.stderr, "FATAL Unsupported execution mode (expected --execute flag)"
        sys.exit(1)
