from . import generic_vendor
from rosette.api import API, DocumentParameters, RosetteException
import json

class RosetteWrapper(generic_vendor.VendorWrapper):
    def __init__(self, settings):
        self.client = API(user_key=settings['api_key'])

    def call_api(self, content):
        params = DocumentParameters()
        params["content"] = content[0:49999] # truncate to first 50000 chars
        res = {}
        try:
            res = self.client.entities(params)
        except RosetteException as exception:
            print(exception)
            res = {"rosette_exception": str(exception)}
        return json.dumps(res)

    def report(self, response_file_name):
        response = self.load_response_json(response_file_name)
        response_with_confidence = {
            'entities': [entity for entity in response['entities'] if 'confidence' in entity]
        }
        response_with_confidence['entities'].sort(key=lambda x: x['confidence'], reverse=True)
        response_without_confidence = {
            'entities': [entity for entity in response['entities'] if 'confidence' not in entity]
        }
        response_without_confidence['entities'].sort(key=lambda x: x['count'], reverse=True)

        report = self.base_report(response_file_name)
        report['entities'] = self.feature_report(response_with_confidence, 'entities', lambda e: e['normalized'] + ' (' + e['type'] + ')')
        report['entities_without_confidence_information'] = self.feature_report(response_with_confidence, 'entities', lambda e: e['normalized'] + ' (' + e['type'] + ')')

        entity_types_of_interest = ['LOCATION', 'PERSON', 'TEMPORAL:DATE', 'ORGANIZATION']
        for entity_type in entity_types_of_interest:
            entities = [entity for entity in response['entities'] if entity['type'] == entity_type]
            report['entities'][entity_type + ' examples'] = [e['normalized'] for e in entities][0:19]

        return report
