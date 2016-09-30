import json
from .base_handler import BaseRestHandler

class VersionHandler(BaseRestHandler):
    def handle_GET(self):
        s = self.create_service()
        self.send_json_response({
            "splunk_version": "",
            "itsi_version": "",
            "es_version": "",
            "addon_version": "",
        })
