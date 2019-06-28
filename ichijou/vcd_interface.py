from pathlib import Path


class VCDInterface(object):

    @staticmethod
    def does_raw_result_exist(benchmark, experiment_type, experiment_directory):
        result_file = Path(experiment_directory, "output", "{0}_{1}_ila_results.vcd".format(benchmark, experiment_type))
        return result_file.exists()

    def extract_results(self, benchmark, experiment_type, experiment_directory, trigger_values):
        return "Hello World"