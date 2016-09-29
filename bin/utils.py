import os
import urllib2

workato_app_name = os.path.basename(os.path.dirname(os.path.dirname(__file__)))

class Request(urllib2.Request):
    def set_method(self,method):
        self.__method=method
    def get_method(self):
        return self.__method
