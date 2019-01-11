from . import generic_vendor
import textrazor
import json
import sys
import textwrap

MAX_SIZE = 200 * 1024

class TextRazorWrapper(generic_vendor.VendorWrapper):
    def __init__(self, settings):
        textrazor.api_key = settings['api_key']
        self.client = textrazor.TextRazor(extractors=["entities", "topics"])

    def call_api(self, content):
        truncated_content = self.__truncate_to_byte_size(content, MAX_SIZE-1)
        response = self.client.analyze(truncated_content) # truncate the content
        return json.dumps(response.json, sort_keys=True, indent=4)

    def report(self, response_file_name, metadata):
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
        report['entities']['in_metadata_count'] = len({e for e in seen if e.lower() in metadata.lower()})
        report['entities']['in_metadata_percent'] = report['entities']['in_metadata_count']/report['entities']['count']

        # report on topics
        report['topics'] = {}
        topics = list(response.topics())
        topics.sort(key=lambda x: x.score, reverse=True)
        report['topics']['count'] = len(topics)
        report['topics']['examples'] = []
        for topic in topics:
            if len(report['topics']['examples']) < 5:
                report['topics']['examples'].append(topic.label)

        return report

    # Ugly way to truncate text to a specific size in *bytes*
    # (I did not find any other safe way of doing it with text in multi-bytes
    # characters encoding)
    def __truncate_to_byte_size(self, text, size):
        res = ''
        while sys.getsizeof(res) < size and len(text) > 0:
            res, text = res+text[:1], text[1:]
        return res
