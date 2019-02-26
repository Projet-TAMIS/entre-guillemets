from . import generic_vendor
import json

# The Comprehend Custom Classification vendor analyzer is different from others
# because there is no API to ask classification of a single document. Instead,
# a classification job must be run (manually or by other means) and the resulting
# predictions file (in the jsonl format) must be provided to Entre Guillemets,
# as the way to get classifications.

class AmazonComprehendCustomClassification(generic_vendor.VendorWrapper):
    stores_results = False

    def __init__(self, settings):
        # instead of creating a client object like we do for other vendors,
        # we load and parse the predictions from the Comprehend jsonl result file
        with open(settings['predictions_file']) as data:
            prediction_data = data.read()
        prediction_lines = prediction_data.split("\n")
        self.predictions = {}
        for prediction_line in [line for line in prediction_lines if (line is not None and len(line) > 0)]:
            prediction = json.loads(prediction_line)
            self.predictions[prediction['File']] = prediction['Classes']

    def call_api(self, content):
        # no need for that, as we have loaded all the results in self.predictions
        pass

    def report(self, response_file_name, metadata, original_file):
        report = self.base_report(response_file_name)
        report['categories'] = {}
        report['categories']['BISAC'] = [klass['Name']+ ' (' + str(klass['Score']) + ')' for klass in self.predictions[original_file]]
        return report
