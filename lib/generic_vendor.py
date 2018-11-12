import json

class VendorWrapper:
    def process(self, input_file_name, output_file_name):
        with open(input_file_name) as input_file:
            content = input_file.read()
        output = self.call_api(content)
        with open(output_file_name, 'w') as output_file:
            output_file.write(output)

    def load_response_json(self, file_name):
        with open(file_name) as data:
            json_data = data.read()
        return json.loads(json_data)

    def feature_report(self, response, feature_name, flattener):
        report = {}
        features = response[feature_name]
        report['count'] = len(features)
        report['examples'] = []
        report['detailed_examples'] = []
        for f in features[0:19]:
            report['examples'].append(flattener(f))
        for f in features[0:4]:
            report['detailed_examples'].append(f)
        return report
