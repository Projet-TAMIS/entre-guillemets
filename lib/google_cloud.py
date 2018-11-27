from . import generic_vendor
import json
from google.cloud import language
from google.oauth2 import service_account
from google.cloud.language import enums
from google.cloud.language import types
from google.protobuf.json_format import MessageToJson

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

    def report(self, response_file_name):
        response = self.load_response_json(response_file_name)
        response['entities'].sort(key=lambda x: x['salience'], reverse=True)
        report = self.base_report(response_file_name)
        report['entities'] = self.feature_report(response, 'entities', lambda e: e['name'] + ' (' + e['type'] + ')')
        return report
