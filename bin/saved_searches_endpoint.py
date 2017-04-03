import json
import time
from splunklib import results as results_lib
from .base_handler import BaseRestHandler
from .utils import workato_app_name
from .alert_action_utils import add_callback, remove_callback, has_workato_alert_action


class SavedSearchesHandler(BaseRestHandler):

    def handle_GET(self):
        s = self.create_service()
        saved_searches = s.saved_searches.list(search="is_scheduled=0")

        def filter(search):
            if search.access.app == workato_app_name:
                return False
            if search.name.startswith("__"):
                return False
            return True
        self.send_json_response(
            [search.name for search in saved_searches if filter(search)]
        )

    def handle_POST(self):
        payload = json.loads(self.request['payload'])
        s = self.create_service()
        saved_search = s.saved_searches[payload['search_name']]

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

        results = run_splunk_search("savedsearch %s" % saved_search.name)

        self.send_json_response({
            "results": results,
        })
