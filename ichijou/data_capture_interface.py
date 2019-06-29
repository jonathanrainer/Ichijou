from pathlib import Path
from openpyxl import load_workbook


class DataCaptureInterface(object):

    results_file = None
    experiment_type_mapper = {
        "nc": "No Cache",
        "sc": "Standard Cache",
        "cc": "Complex Cache"
    }

    def __init__(self, results_file):
        self.results_file = Path(results_file)

    def result_present(self, benchmark_name, experiment_type):
        workbook = load_workbook(self.results_file)
        return any([x.value == benchmark_name for x in workbook.get_sheet_by_name(
            self.experiment_type_mapper[experiment_type]
        )["B"]])

    def store_result(self, benchmark_name, experiment_type, result):
        workbook = load_workbook(self.results_file)
        sheet = workbook.get_sheet_by_name(self.experiment_type_mapper[experiment_type])
        sheet.append(["", benchmark_name, result])
        workbook.save(self.results_file)