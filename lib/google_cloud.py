from . import generic_vendor
import json
from google.cloud import language
from google.oauth2 import service_account
from google.cloud.language import enums
from google.cloud.language import types
from google.protobuf.json_format import MessageToJson
import functools

class GoogleCloudWrapper(generic_vendor.VendorWrapper):
    def __init__(self, settings):
        credentials = service_account.Credentials.from_service_account_file(settings['credentials_file'])
        self.client = language.LanguageServiceClient(credentials=credentials)

    def call_api(self, content):
        document = types.Document(
            content=content,
            type=enums.Document.Type.PLAIN_TEXT)
        response = self.client.analyze_entities(
             document=document,
             encoding_type='UTF8',
        )
        return MessageToJson(response)

    def report(self, response_file_name, metadata):
        response = self.load_response_json(response_file_name)
        report = self.base_report(response_file_name)

        if 'entities' in response:
            response['entities'].sort(key=lambda x: x['salience'], reverse=True)
            report['entities'] = self.feature_report(response, 'entities', lambda e: e['name'] + ' (' + e['type'] + ')', metadata, lambda e: e['name'])

            entity_types_of_interest = ['LOCATION', 'PERSON', 'EVENT']
            for entity_type in entity_types_of_interest:
                entities = [entity for entity in response['entities'] if entity['type'] == entity_type]
                entity_names = [e['name'] for e in entities]
                unique_entities = functools.reduce(lambda l, x: l+[x] if x not in l else l, entity_names, [])
                  # the above line removes duplicates and keeps order (explanations: https://stackoverflow.com/a/37163210)
                report['entities'][entity_type + ' examples'] = unique_entities[0:19]
        else:
            report['error'] = 'No entities found'

        return report
