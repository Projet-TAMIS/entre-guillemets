from . import generic_vendor
import json
from watson_developer_cloud import NaturalLanguageUnderstandingV1, WatsonException
from watson_developer_cloud.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, CategoriesOptions, ConceptsOptions

class IBMWatsonWrapper(generic_vendor.VendorWrapper):
    def __init__(self, settings):
        self.client = NaturalLanguageUnderstandingV1(
            version='2018-03-16',
            url=settings['api_url'],
            iam_apikey=settings['api_key'])

    def call_api(self, content):
        try:
            response = self.client.analyze(
                text=content,
                features=Features(entities=EntitiesOptions(),
                          keywords=KeywordsOptions(),
                          categories=CategoriesOptions(),
                          concepts=ConceptsOptions())).get_result()
        except WatsonException as exception:
            print(exception)
            response = {"ibm_exception": str(exception)}
        return json.dumps(response, sort_keys=True, indent=4)

    def report(self, response_file_name):
        response = self.load_response_json(response_file_name)
        report = self.base_report(response_file_name)

        if 'ibm_exception' in response:
            report['error'] = response['ibm_exception']
        else:
            report['entities'] = self.feature_report(response, 'entities', lambda e: e['text'] + ' (' + e['type'] + ')')
            report['categories'] = self.feature_report(response, 'categories', lambda c: c['label'])
            report['keywords'] = self.feature_report(response, 'keywords', lambda k: k['text'])
            report['concepts'] = self.feature_report(response, 'concepts', lambda c: c['text'])

            entity_types_of_interest = ['Location', 'Person', 'Date']
            for entity_type in entity_types_of_interest:
                entities = [entity for entity in response['entities'] if entity['type'] == entity_type]
                report['entities'][entity_type + ' examples'] = [e['text'] for e in entities][0:19]

        return report
