from splunk import auth, search
import splunk.rest
import logging as logger
import splunk.bundle as bundle
import httplib2, urllib, os, time
import json
import splunklib.client as client
from splunklib.binding import _spliturl as spliturl
from splunklib.binding import namespace as namespace
import base64
import random

class SubscriptionHandler(splunk.rest.BaseRestHandler):
    def handle_GET(self):
        self.request['payload'] = '{"management_url": "http://cultusgame.de:8090/", "callback_url": "haleloe", "object_type": "raw_event"}'
        self.handle_POST()
    def create_service(self,management_url):
        scheme, host, port, path = spliturl(management_url)
        self.response.setStatus(200)
        self.response.setHeader('content-type', 'application/json')
        token = self.request["headers"].get("authorization", "")[6:]
        username, password = base64.b64decode(token).split(':')
        s = client.Service(
            username=username,
            password=password,
            port=port,
            scheme=scheme,
            host=host)
        s.login()
        return s
    def handle_POST(self):
        payload = json.loads(self.request['payload'])
        stanza_name = "%s"%random.randint(1, 100000000)
        s = self.create_service(payload['management_url'])
        s.confs.create('subscriptions').create(
            stanza_name,
            namespace=namespace(sharing="app",app="workato"),
            callback_url=payload['callback_url'],
            object_type=payload['object_type']
            )
        self.response.setStatus(200)
        self.response.setHeader('content-type', 'application/json')
        self.response.write(json.dumps({
            "name": stanza_name
        }))
    def handle_DELETE(self):
        payload = json.loads(self.request['payload'])
        s = self.create_service(payload['management_url'])
        s.confs.create('subscriptions').delete(payload["subscription_name"])
        self.response.setStatus(200)
