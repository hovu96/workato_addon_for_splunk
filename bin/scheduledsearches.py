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
from base_handler import BaseRestHandler

workato_app_name = os.path.basename(os.path.dirname(os.path.dirname(__file__)))

class ScheduledSearchesHandler(BaseRestHandler):
    def handle_GET(self):
        payload = json.loads(self.request['payload'])
        s = self.create_service()
        saved_searches = s.saved_searches.list(search="is_scheduled=1")
        self.response.setStatus(200)
        self.response.setHeader('content-type', 'application/json')
        self.response.write(json.dumps(
            [ search.name for search in saved_searches if search.access.app!=workato_app_name ]
        ))
    def handle_POST(self):
        payload = json.loads(self.request['payload'])
        s = self.create_service()
        saved_search = s.saved_searches[payload['search_name']]
        if 'action.workato.param.callback_url' in saved_search.content:
            if saved_search['action.workato.param.callback_url']:
                raise Exception('other endpoint (%s) already registered' % saved_search['action.workato.param.callback_url'])
        kwargs = {
            "actions": "workato",
            "action.workato.param.callback_url": payload['callback_url'],
            }
        saved_search.update(**kwargs)
        self.response.setStatus(200)
        self.response.setHeader('content-type', 'application/json')
        self.response.write(json.dumps({
            "id": payload['callback_url']
        }))
    def handle_DELETE(self):
        payload = json.loads(self.request['payload'])
        s = self.create_service()
        saved_search = s.saved_searches[payload['search_name']]
        if 'action.workato.param.callback_url' in saved_search.content:
            if saved_search['action.workato.param.callback_url'] != payload['callback_url']:
                raise Exception('other endpoint (%s) already registered' % saved_search['action.workato.param.callback_url'])
        kwargs = {
            "actions": "",
            "action.workato.param.callback_url": "",
            }
        saved_search.update(**kwargs)
        self.response.setStatus(200)
