from . import generic_vendor
import json
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, CategoriesOptions, ConceptsOptions

class IBMWatsonWrapper(generic_vendor.VendorWrapper):
    def __init__(self, settings):
        self.client = NaturalLanguageUnderstandingV1(
            version='2018-03-16',
            url=settings['api_url'],
            iam_apikey=settings['api_key'])

    def call_api(self, content):
        response = self.client.analyze(
            text=content,
            features=Features(entities=EntitiesOptions(),
                      keywords=KeywordsOptions(),
                      categories=CategoriesOptions(),
                      concepts=ConceptsOptions())).get_result()
        return json.dumps(response)

    def report(self, response_file_name):
        response = self.load_response_json(response_file_name)
        report = self.base_report(response_file_name)

        report['entities'] = self.feature_report(response, 'entities', lambda e: e['text'] + ' (' + e['type'] + ')')
        report['categories'] = self.feature_report(response, 'categories', lambda c: c['label'])
        report['keywords'] = self.feature_report(response, 'keywords', lambda k: k['text'])
        report['concepts'] = self.feature_report(response, 'concepts', lambda c: c['text'])

        return report
