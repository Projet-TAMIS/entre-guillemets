import os
import re

class Classifications():
    def __init__(self):
        self.__load_bisac()

    def __load_bisac(self):
        bisac_file = os.path.join(os.path.dirname(__file__), 'bisac.csv')
        with open(bisac_file) as data:
            lines = data.read().split("\n")
            self.bisac = {}
            for line in lines:
                code = line[0:9]
                label = line[10:]
                self.bisac[code] = label

    def add_bisac_label_to_subject(self, subject):
        return subject + ' ' + self.bisac.get(subject, '???')

    def replace_bisac_code_with_subjects(self, content):
        bisac_code = re.match(r'[A-Z]{3}[0-9]{6}', content)
        if bisac_code:
            return content.replace(bisac_code[0], self.add_bisac_label_to_subject(bisac_code[0]))
        else:
            return content
