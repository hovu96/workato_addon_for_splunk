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

class BaseRestHandler(splunk.rest.BaseRestHandler):
    def create_service(self):
        management_url = "https://"+self.request["headers"]["host"]+"/"
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
