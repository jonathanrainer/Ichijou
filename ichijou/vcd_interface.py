import re

from pathlib import Path
from Verilog_VCD.Verilog_VCD import parse_vcd


class VCDInterface(object):

    probes = [
        "k_top/system_ila_0/inst/probe9_1[31:0]",
        "k_top/system_ila_0/inst/probe6_1[31:0]",
        "k_top/system_ila_0/inst/probe7_1[31:0]",
        "k_top/system_ila_0/inst/probe8_1[31:0]"
    ]

    @staticmethod
    def get_vcd_file_name(experiment_directory, benchmark, experiment_type, position):
        return Path(experiment_directory, "results", "{}_{}_ila_results_{}.vcd".format(benchmark, experiment_type,
                                                                                       position))

    @staticmethod
    def does_raw_result_exist(benchmark, experiment_type, experiment_directory):
        result_file_start = Path(experiment_directory, "results", "{0}_{1}_ila_results_start.vcd".format(
            benchmark, experiment_type))
        result_file_end = Path(experiment_directory, "results", "{0}_{1}_ila_results_end.vcd".format(
            benchmark,experiment_type))
        return result_file_start.exists() and result_file_end.exists()

    def extract_results(self, benchmark, experiment_type, experiment_directory, addr_values_to_find):
        start_vcd_file = parse_vcd(self.get_vcd_file_name(experiment_directory, benchmark, experiment_type, "start"))
        start_addr_time = self.get_addr_time(start_vcd_file, addr_values_to_find[0], 0, "cc" in experiment_type)
        start_time = self.get_start_time_from_addr_time(start_addr_time, start_vcd_file)
        end_vcd_file = parse_vcd(self.get_vcd_file_name(experiment_directory, benchmark, experiment_type, "end"))
        end_addr_time = self.get_addr_time(end_vcd_file, addr_values_to_find[1], 3, False)
        end_time = self.get_start_time_from_addr_time(end_addr_time, end_vcd_file)
        results = [end_time[0] - start_time[0]]
        counter_values = self.extract_counter_values(start_time[1], end_time[1], start_vcd_file, end_vcd_file)
        return results + counter_values

    @staticmethod
    def get_addr_time(vcd_file, addr_value, offset, last_flag):
        addr_values = \
            [x['tv'] for x in vcd_file.values() if
             x['nets'][0]["name"] == "k_top/system_ila_0/inst/probe1_1[31:0]"][0]
        if last_flag:
            return [x for x in addr_values if int(x[1], base=2) == int(addr_value, base=16)][-1][0]
        else:
            return [x for x in addr_values if int(x[1], base=2) == int(addr_value, base=16)][offset][0]

    @staticmethod
    def get_start_time_from_addr_time(addr_time, vcd_file):
        gnt_values = \
            [x['tv'] for x in vcd_file.values() if x['nets'][0]["name"] == "k_top/system_ila_0/inst/probe4_1"][0]
        gnt_time = [y for y in gnt_values if y[0] >= addr_time][0][0]
        req_values = \
            [x['tv'] for x in vcd_file.values() if x['nets'][0]["name"] == "k_top/system_ila_0/inst/probe2_1"][0]
        start_of_req = [x for x in req_values if x[0] < gnt_time][-1][0]
        counter_values = \
            [x['tv'] for x in vcd_file.values() if x['nets'][0]["name"] == "k_top/system_ila_0/inst/probe3_1[31:0]"][0]
        exact_match = [(int(y[1], base=2), y[0]) for y in counter_values if y[0] == start_of_req]
        if not exact_match:
            return [(int(y[1], base=2), y[0]) for y in counter_values if y[0] <= start_of_req][-1]
        else:
            return exact_match[0]

    def extract_counter_values(self, start_ila_time, end_ila_time, start_vcd_file, end_vcd_file):
        results = []
        for probe in self.probes:
            start_counter_values = [x['tv'] for x in start_vcd_file.values() if x['nets'][0]["name"] == probe][0]
            end_counter_values = [x['tv'] for x in end_vcd_file.values() if x['nets'][0]["name"] == probe][0]
            start_value = int([x for x in start_counter_values if x[0] <= start_ila_time][-1][1], base=2)
            end_value = int([x for x in end_counter_values if x[0] <= end_ila_time][-1][1], base=2)
            results.append(end_value - start_value)
        return results
