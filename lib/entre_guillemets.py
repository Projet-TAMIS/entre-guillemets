from jinja2 import FileSystemLoader, Environment
from . import textrazor
from . import rosette
import os
import json

VENDORS = {
    'textrazor': textrazor.TextRazorWrapper,
    'rosette': rosette.RosetteWrapper
}

class EntreGuillemets:
    def __init__(self, settings):
        self.settings = settings
        self.__ensure_directory_exists(self.settings['output_files_dir'])
        self.__ensure_directory_exists(self.settings['report_dir'])
        loader = FileSystemLoader('.')
        env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
        self.report_template = env.get_template(self.settings['template_file'])

    def run(self):
        print("Getting API responses...")
        all_files = self.__list_input_files()
        for vendor_name in self.settings['vendors'].keys():
            vendor = VENDORS[vendor_name](self.settings['vendors'][vendor_name])
            for file in all_files:
                if self.__already_processed(file, vendor_name):
                    print("Already processed " + file + " with " + vendor_name)
                    continue
                input_file_name = os.path.join(self.settings['input_files_dir'], file)
                output_file_name = self.__output_file_name(file, vendor_name)
                print("Processing " + file + " with " + vendor_name)
                vendor.process(input_file_name, output_file_name)

    def report(self):
        print("Creating report data...")
        all_files = self.__list_input_files()
        file_refs = self.__load_file_refs(all_files)
        for vendor_name in self.settings['vendors'].keys():
            vendor = VENDORS[vendor_name](self.settings['vendors'][vendor_name])
            vendor_report = {}
            for file in all_files:
                if self.__already_processed(file, vendor_name):
                    vendor_response_file_name = self.__output_file_name(file, vendor_name)
                    vendor_report[os.path.basename(file)] = vendor.report(vendor_response_file_name)
                    print("Analyzing and creating report for " + file)
            self.__build_vendor_report(vendor_name, vendor_report, file_refs)

        print("Outputting report to HTML...")
        # TODO!

    def __list_input_files(self):
        files = os.listdir(self.settings['input_files_dir'])
        return [file for file in files if os.path.splitext(file)[1].lower() == '.txt']

    def __already_processed(self, file, vendor_name):
        dest_name = self.__output_file_name(file, vendor_name)
        return os.path.isfile(dest_name)

    def __output_file_name(self, file, vendor_name):
        base_name = os.path.splitext(file)[0]
        return os.path.join(self.settings['output_files_dir'], base_name + "_" + vendor_name + ".json")

    def __ensure_directory_exists(self, directory):
        if not os.path.isdir(directory):
            os.mkdir(directory)

    def __load_file_refs(self, all_files):
        refs = {}
        for file_name in all_files:
            ref_file_name = os.path.join(self.settings['input_files_dir'], file_name + '.json')
            if os.path.isfile(ref_file_name):
                with open(ref_file_name) as data:
                    refs[os.path.basename(file_name)] = json.load(data)
            else:
                refs[os.path.basename(file_name)] = { "name": file_name }
        return refs

    def __build_vendor_report(self, vendor_name, vendor_report, file_refs):
        report = self.report_template.render(vendor_name=vendor_name, vendor_report=vendor_report, file_refs=file_refs)
        with open(os.path.join(self.settings['report_dir'], vendor_name + '.html'), 'w') as r:
            r.write(report)
