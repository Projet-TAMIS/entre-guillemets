from . import generic_vendor
import textrazor
import json

class TextRazorWrapper(generic_vendor.VendorWrapper):
    def __init__(self, settings):
        textrazor.api_key = settings['api_key']
        self.client = textrazor.TextRazor(extractors=["entities", "topics"])

    def call_api(self, content):
        response = self.client.analyze(content)
        return json.dumps(response.json)

    def report(self, response_file_name):
        json_response = self.load_response_json(response_file_name)
        response = textrazor.TextRazorResponse(json_response)
        report = self.base_report(response_file_name)

        # report on entities
        report['entities'] = {}
        entities = list(response.entities())
        entities.sort(key=lambda x: x.relevance_score, reverse=True)
        report['entities']['count'] = len(entities)
        report['entities']['examples'] = []
        report['entities']['detailed_examples'] = []
        entity_types_of_interest = [
            '/location/location',
            '/people/person',
            '/organization/organization',
            '/time/event'
        ]
        for entity_type in entity_types_of_interest:
            report['entities'][entity_type] = []
        seen = set()
        for entity in entities:
            if entity.id not in seen:
                if len(report['entities']['examples']) < 20:
                    report['entities']['examples'].append(entity.id)
                if len(report['entities']['detailed_examples']) < 5:
                    report['entities']['detailed_examples'].append(entity.json)
                for entity_type in entity_types_of_interest:
                    if (entity_type in entity.freebase_types):
                        report['entities'][entity_type].append(entity.id)
                seen.add(entity.id)

        # report on categories
        report['topics'] = {}
        topics = list(response.topics())
        topics.sort(key=lambda x: x.score, reverse=True)
        report['topics']['count'] = len(topics)
        report['topics']['examples'] = []
        for topic in topics:
            if len(report['topics']['examples']) < 5:
                report['topics']['examples'].append(topic.label)

        return report
