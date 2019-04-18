from . import classifications

class Plugin(classifications.Classifications):
    def apply(self, data):
        if 'products' in data:
            if 'subjects' in data['products'][0]:
                if 'bisac' in data['products'][0]['subjects']:
                    data['products'][0]['subjects']['bisac'] = [self.add_bisac_label_to_subject(subject) for subject in data['products'][0]['subjects']['bisac']]
        if 'categories' in data:
            if 'BISAC' in data['categories']:
                data['categories']['BISAC'] = [self.replace_bisac_code_with_subjects(entry) for entry in data['categories']['BISAC']]
        return data
