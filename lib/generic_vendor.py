import json
import math

class VendorWrapper:
    stores_results = True

    def process(self, input_file_name, output_file_name):
        with open(input_file_name) as input_file:
            content = input_file.read()
        output = self.call_api(content)
        if output is not None and len(output) > 0:
            with open(output_file_name, 'w') as output_file:
                output_file.write(output)

    def load_response_json(self, file_name):
        with open(file_name) as data:
            json_data = data.read()
        return json.loads(json_data)

    # Creates a standard report for a feature based on the report
    #
    # flattener is a function that converts the feature dict to a single string,
    # used for displayed the feature to the user
    #
    # Optionnaly, the standard report can also include metrics to indicate if the
    # found features were already in the metadata. To do this, include
    # - metadata : a String for the metadata to be checked
    # - text_extractor : a function similar to flattener, but that converts the
    #   feature dict to a single string used for comparison with the metadata
    def feature_report(self, response, feature_name, flattener, metadata=None, text_extractor=None):
        report = {}
        features = response[feature_name]
        report['count'] = len(features)

        report['examples'] = []
        report['detailed_examples'] = []
        for f in features[0:19]:
            report['examples'].append(flattener(f))
        for f in features[0:4]:
            report['detailed_examples'].append(f)

        if metadata is not None and text_extractor is not None:
            report['in_metadata_count'] = len([feature for feature in features if text_extractor(feature).lower() in metadata.lower()])
            if report['count'] is not 0:
                report['in_metadata_percent'] = report['in_metadata_count'] / report['count']
            else:
                report['in_metadata_percent'] = math.nan

        return report

    def base_report(self, response_file_name):
        return { 'source_file': response_file_name }
