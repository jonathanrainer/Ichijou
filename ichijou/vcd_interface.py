from pathlib import Path
from Verilog_VCD.Verilog_VCD import parse_vcd


class VCDInterface(object):

    @staticmethod
    def does_raw_result_exist(benchmark, experiment_type, experiment_directory):
        result_file = Path(experiment_directory, "results", "{0}_{1}_ila_results.vcd".format(benchmark, experiment_type))
        return result_file.exists()

    def extract_results(self, benchmark, experiment_type, experiment_directory, addr_values_to_find):
        vcd_file = parse_vcd(Path(experiment_directory, "results",
                                  "{}_{}_ila_results.vcd".format(benchmark, experiment_type)))
        start_addr_time = self.get_addr_time(vcd_file, addr_values_to_find[0], 0)
        start_time = self.get_start_time_from_addr_time(start_addr_time, vcd_file)
        end_addr_time = self.get_addr_time(vcd_file, addr_values_to_find[1], 3)
        end_time = self.get_start_time_from_addr_time(end_addr_time, vcd_file)
        return end_time - start_time

    @staticmethod
    def get_addr_time(vcd_file, addr_value, offset):
        addr_values = \
            [x['tv'] for x in vcd_file.values() if x['nets'][0]["name"] == "k_top/system_ila_0/inst/probe1_1[15:0]"][0]
        return [x for x in addr_values if int(x[1], base=2) == int(addr_value, base=16)][offset][0]

    @staticmethod
    def get_start_time_from_addr_time(addr_time, vcd_file):
        gnt_values = \
            [x['tv'] for x in vcd_file.values() if x['nets'][0]["name"] == "k_top/system_ila_0/inst/probe4_1"][0]
        gnt_time = [y for y in gnt_values if y[0] > addr_time][0][0]
        req_values = \
            [x['tv'] for x in vcd_file.values() if x['nets'][0]["name"] == "k_top/system_ila_0/inst/probe2_1"][0]
        start_of_req = [x for x in req_values if x[0] < gnt_time][-1][0]
        counter_values = \
            [x['tv'] for x in vcd_file.values() if x['nets'][0]["name"] == "k_top/system_ila_0/inst/probe3_1[31:0]"][0]
        return [int(y[1], base=2) for y in counter_values if y[0] == start_of_req][0]
