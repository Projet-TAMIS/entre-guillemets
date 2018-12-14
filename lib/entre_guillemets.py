from jinja2 import FileSystemLoader, Environment
from . import textrazor
from . import ibm_watson
from . import google_cloud
from . import rosette
import os
import json
import datetime
import xlsxwriter
import pandas as pd
from pandas.io.json import json_normalize

VENDORS = {
    'textrazor': textrazor.TextRazorWrapper,
    'ibm_watson': ibm_watson.IBMWatsonWrapper,
    'google_cloud': google_cloud.GoogleCloudWrapper,
    'rosette': rosette.RosetteWrapper
}

class EntreGuillemets:
    def __init__(self, settings):
        self.settings = settings
        self.__ensure_directory_exists(self.settings['output_files_dir'])
        self.__ensure_directory_exists(self.settings['report_dir'])

        # for Jinja2 templating
        loader = FileSystemLoader('.')
        env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
        self.global_report_template = env.get_template(self.settings['global_template_file'])
        self.vendor_report_template = env.get_template(self.settings['vendor_template_file'])

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
        global_report = {}
        for vendor_name in self.settings['vendors'].keys():
            vendor = VENDORS[vendor_name](self.settings['vendors'][vendor_name])
            vendor_report = {}
            for file in all_files:
                if self.__already_processed(file, vendor_name):
                    vendor_response_file_name = self.__output_file_name(file, vendor_name)
                    vendor_report[os.path.basename(file)] = vendor.report(vendor_response_file_name)
                    print("Analyzing and creating report for " + file + " (" + vendor_name + ")")
            self.__build_vendor_report(vendor_name, vendor_report, file_refs)
            global_report[vendor_name] = vendor_report

        print("Outputting report to HTML...")
        self.__build_global_report(global_report, all_files, file_refs)
        self.__build_global_xlsx_report(global_report, all_files, file_refs)

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
        meta = {
            "vendor_name": vendor_name,
            "report_date": datetime.datetime.now(),
            "features": vendor_report[list(vendor_report.keys())[0]].keys(),
            "corpus_size": len(vendor_report.keys()),
            "global_report_path": 'index.html'
        }
        report = self.vendor_report_template.render(meta=meta, vendor_report=vendor_report, file_refs=file_refs)
        with open(os.path.join(self.settings['report_dir'], vendor_name + '.html'), 'w') as r:
            r.write(report)

    def __build_global_report(self, global_report, all_files, file_refs):
        meta = {
            "report_date": datetime.datetime.now(),
            "vendors": [
                {
                    'name': vendor,
                    'report_path': vendor + '.html'
                }
            for vendor in global_report]
        }

        report = self.global_report_template.render(meta=meta, report=global_report, files=all_files, file_refs=file_refs)
        with open(os.path.join(self.settings['report_dir'], 'index.html'), 'w') as r:
            r.write(report)

    def __build_global_xlsx_report(self, global_report, all_files, file_refs):
        ref_df = pd.DataFrame.from_dict({ k: self.__flattenize(v['products'][0], 'product') for (k,v) in file_refs.items()}, orient='index')
        writer = pd.ExcelWriter('hello.xlsx', engine='xlsxwriter')
        all_dfs = ref_df
        for vendor in global_report:
            vendor_data = { k: self.__flattenize(v, vendor) for (k,v) in global_report[vendor].items()}
            vendor_df = pd.DataFrame.from_dict(vendor_data, orient='index')
            all_dfs = pd.concat([all_dfs, vendor_df], axis='columns')
        all_dfs.to_excel(writer, sheet_name='Global report')
        writer.save()

    # this will flatten and nested dict objj to a single level
    # dict, where keys are the result of concatenating the nested keys,
    # and values are final str or int node values, or lists converted to
    # multi-lines strs
    def __flattenize(self, objj, base_k):
        res = {}
        if objj.__class__.__name__ == 'dict':
            for k, v in objj.items():
                if v.__class__.__name__ == 'dict':
                    res = self.__flattenize(v, base_k + '.' + k)
                else:
                    res[base_k + '.' + k] = self.__flattenize(v, base_k + '.' + k)
        elif objj.__class__.__name__ == 'list':
            res = "\n".join(map(lambda x: str(x), objj))
        else:
            res = objj
        return res
