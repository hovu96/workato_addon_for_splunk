import sys, os, datetime, json, urllib2
import splunklib.client as client
from splunklib.binding import _spliturl as spliturl
from splunklib.binding import namespace as namespace
import gzip, csv
from alert_action_utils import iterate_callbacks_from_string

def call_workato(payload):

    config = payload.get('configuration')
    callback_urls = config.get('callback_urls')
    if callback_urls is None:
        callback_urls = ""
    callback_urls = list(iterate_callbacks_from_string(callback_urls))

    sid = payload.get('sid')
    def log(level,msg):
        print >> sys.stderr, "%s sid=\"%s\" %s" % (level,sid,msg)
    def log_info(msg):
        log("INFO",msg)
    def log_debug(msg):
        log("DEBUG",msg)
    def log_error(msg):
        log("ERROR",msg)

    alert_count = 0
    callback_url_count = len(callback_urls)
    callback_invocation_attempts = 0
    callback_invocation_errors = 0

    results_file = payload.get('results_file')
    with gzip.open(results_file, 'rb') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            alert_count += 1
            payload = {}
            for name, value in row.iteritems():
                if not name.startswith('__mv'):
                    payload[name]=value
            for callback_url in callback_urls:
                callback_invocation_attempts += 1
                try:
                    req = urllib2.Request(callback_url, json.dumps(payload), {"Content-Type": "application/json"})
                    res = urllib2.urlopen(req)
                    body_bytes = len(str(res.read()))
                    log_info("callback=\"%s\" status=%d body_length=\"%d\"" % (callback_url, res.code, body_bytes))
                except urllib2.HTTPError, e:
                    callback_invocation_errors += 1
                    log_error("callback=\"%s\" error=\"%s\"" % (callback_url, str(e)))

    log_info("alert_count=%d callback_url_count=%d callback_invocation_attempts=%d callback_invocation_errors=%d" % (alert_count, callback_url_count, callback_invocation_attempts, callback_invocation_errors))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        payload = sys.stdin.read()
        payload = json.loads(payload)
        call_workato(payload)
    else:
        print >> sys.stderr, "FATAL Unsupported execution mode (expected --execute flag)"
        sys.exit(1)