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
