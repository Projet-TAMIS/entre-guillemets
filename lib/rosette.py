from . import generic_vendor
from rosette.api import API, DocumentParameters, RosetteException
import json

class RosetteWrapper(generic_vendor.VendorWrapper):
    def __init__(self, settings):
        self.client = API(user_key=settings['api_key'])

    def call_api(self, content):
        params = DocumentParameters()
        params["content"] = content
        res = {}
        try:
            res = {
                "entities": self.client.entities(params),
                "categories": self.client.categories(params)
            }
        except RosetteException as exception:
            print(exception)
            res = {"rosette_exception": str(exception)}

        return json.dumps(res)

    def report(self, response_file_name):
        return { "foo": { "foo": "bar" } }
