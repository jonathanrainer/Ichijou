from pathlib import Path
from Verilog_VCD.Verilog_VCD import parse_vcd


class VCDInterface(object):

    @staticmethod
    def get_addr_time(vcd_file, addr_value, offset, last_flag, addr_probe, zero_valued_probe):
        addr_values = \
            [x['tv'] for x in vcd_file.values() if
             x['nets'][0]["name"] == addr_probe][0]
        if last_flag:
            matching_vals = [x for x in addr_values if int(x[1], base=2) == int(addr_value, base=16)]
            hit_count_values = \
                [x['tv'] for x in vcd_file.values() if
                 x['nets'][0]["name"] == zero_valued_probe][0]
            for match in matching_vals:
                if len(hit_count_values) == 1 or hit_count_values[1][0] > match[0]:
                    return match[0]
        else:
            return [x for x in addr_values if int(x[1], base=2) == int(addr_value, base=16)][offset][0]

    @staticmethod
    def get_start_time_from_addr_time(addr_time, vcd_file, gnt_probe, req_probe, counter_probe):
        gnt_values = \
            [x['tv'] for x in vcd_file.values() if x['nets'][0]["name"] == gnt_probe][0]
        gnt_time = [y for y in gnt_values if y[0] >= addr_time][0][0]
        req_values = \
            [x['tv'] for x in vcd_file.values() if x['nets'][0]["name"] == req_probe][0]
        start_of_req = [x for x in req_values if x[0] < gnt_time][-1][0]
        counter_values = \
            [x['tv'] for x in vcd_file.values() if x['nets'][0]["name"] == counter_probe][0]
        exact_match = [(int(y[1], base=2), y[0]) for y in counter_values if y[0] == start_of_req]
        if not exact_match:
            return [(int(y[1], base=2), y[0]) for y in counter_values if y[0] <= start_of_req][-1]
        else:
            return exact_match[0]


class VCDRuntimeInterface(VCDInterface):

    cc_probes = [
        "k_top/system_ila_0/inst/probe7_1[31:0]",   # Instruction (Count)
        "k_top/system_ila_0/inst/probe9_1[31:0]",   # Number of Cache Hits (Cache Perspective)
        "k_top/system_ila_0/inst/probe10_1[31:0]",  # Number of Cache Misses (Cache Perspective)
        "k_top/system_ila_0/inst/probe11_1[31:0]",  # Number of Cache Hits (Loads + No Pre-Emptive)
        "k_top/system_ila_0/inst/probe12_1[31:0]",  # Number of Cache Hits (Loads + Pre-Emptive Hit)
        "k_top/system_ila_0/inst/probe13_1[31:0]",  # Number of Cache Hits (Loads + Pre-Emptive Miss)
        "k_top/system_ila_0/inst/probe14_1[31:0]",  # Number of Cache Hits (Store + No Pre-Emptive)
        "k_top/system_ila_0/inst/probe15_1[31:0]",  # Number of Cache Hits (Store + Pre-Emptive Hit)
        "k_top/system_ila_0/inst/probe16_1[31:0]",  # Number of Cache Hits (Store + Pre-Emptive Miss)
        "k_top/system_ila_0/inst/probe17_1[31:0]",  # Number of Cache Misses (Loads + No Pre-Emptive)
        "k_top/system_ila_0/inst/probe18_1[31:0]",  # Number of Cache Misses (Stores + No Pre-Emptive)
        "k_top/system_ila_0/inst/probe19_1[31:0]",  # Number of Writebacks (Loads)
        "k_top/system_ila_0/inst/probe20_1[31:0]",  # Number of Writebacks (Stores)
        "k_top/system_ila_0/inst/probe21_1[31:0]",  # Number of Pre-Emptive Writebacks (Loads)
        "k_top/system_ila_0/inst/probe22_1[31:0]",  # Number of Pre-Emptive Writebacks (Stores)
    ]

    sc_probes = [
        "k_top/system_ila_0/inst/probe7_1[31:0]",    # Instruction Count
        "k_top/system_ila_0/inst/probe6_1[31:0]",    # Number of Memory Operations (CPU Perspective)
        "k_top/system_ila_0/inst/probe8_1[31:0]",    # Number of Cache Hits (Loads)
        "k_top/system_ila_0/inst/probe9_1[31:0]",    # Number of Cache Hits (Stores)
        "k_top/system_ila_0/inst/probe10_1[31:0]",    # Number of Cache Misses (Loads)
        "k_top/system_ila_0/inst/probe11_1[31:0]",    # Number of Cache Misses (Stores)
        "k_top/system_ila_0/inst/probe12_1[31:0]",  # Number of Cache Writebacks (Loads)
        "k_top/system_ila_0/inst/probe13_1[31:0]",  # Number of Cache Writebacks (Stores)
    ]

    nc_probes = [
        "k_top/system_ila_0/inst/probe9_1[31:0]",  # Instruction Count
        "k_top/system_ila_0/inst/probe6_1[31:0]",  # Number of Memory Operations
        "k_top/system_ila_0/inst/probe7_1[31:0]",  # Number of Cache Hits
        "k_top/system_ila_0/inst/probe8_1[31:0]",  # Number of Cache Misses
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
            benchmark, experiment_type))
        return result_file_start.exists() and result_file_end.exists()

    def extract_results(self, benchmark, experiment_type, experiment_directory, addr_values_to_find):
        start_vcd_file = parse_vcd(self.get_vcd_file_name(experiment_directory, benchmark, experiment_type, "start"))
        start_addr_time = self.get_addr_time(start_vcd_file, addr_values_to_find[0], 0, "cc" in experiment_type,
                                             "k_top/system_ila_0/inst/probe1_1[31:0]",
                                             "k_top/system_ila_0/inst/probe8_1[31:0]")
        start_time = self.get_start_time_from_addr_time(start_addr_time, start_vcd_file,
                                                        "k_top/system_ila_0/inst/probe4_1",
                                                        "k_top/system_ila_0/inst/probe2_1",
                                                        "k_top/system_ila_0/inst/probe3_1[31:0]")
        end_vcd_file = parse_vcd(self.get_vcd_file_name(experiment_directory, benchmark, experiment_type, "end"))
        end_addr_time = self.get_addr_time(end_vcd_file, addr_values_to_find[1], 3, False,
                                           "k_top/system_ila_0/inst/probe1_1[31:0]",
                                           "k_top/system_ila_0/inst/probe8_1[31:0]")
        end_time = self.get_start_time_from_addr_time(end_addr_time, end_vcd_file, "k_top/system_ila_0/inst/probe4_1",
                                                      "k_top/system_ila_0/inst/probe2_1",
                                                      "k_top/system_ila_0/inst/probe3_1[31:0]")
        results = [end_time[0] - start_time[0]]
        counter_values = self.extract_counter_values(start_time[1], end_time[1], start_vcd_file, end_vcd_file,
                                                     experiment_type)
        if experiment_type in ["cc_dm", "cc_nway"]:
            counter_values = [counter_values[0]] + [counter_values[1] + counter_values[2]] + counter_values[1:]
        return results + counter_values + [start_time[0]]

    def extract_counter_values(self, start_ila_time, end_ila_time, start_vcd_file, end_vcd_file, experiment_type):
        results = []
        if "cc" in experiment_type:
            probes = self.cc_probes
        elif "sc" in experiment_type:
            probes = self.sc_probes
        else:
            probes = self.nc_probes
        for probe in probes:
            start_counter_values = [x['tv'] for x in start_vcd_file.values() if x['nets'][0]["name"] == probe][0]
            end_counter_values = [x['tv'] for x in end_vcd_file.values() if x['nets'][0]["name"] == probe][0]
            start_value = int([x for x in start_counter_values if x[0] <= start_ila_time][-1][1], base=2)
            end_value = int([x for x in end_counter_values if x[0] <= end_ila_time][-1][1], base=2)
            results.append(end_value - start_value)
        return results


class VCDMGInterface(VCDInterface):

    @staticmethod
    def get_vcd_file_name(experiment_directory, measure_type):
        return Path(experiment_directory, "results", "{}_ila_results.vcd".format(measure_type))

    @staticmethod
    def does_raw_result_exist(benchmark, experiment_type, experiment_directory):
        result_file_gap = Path(experiment_directory, "results", "gap_ila_results.vcd".format(
            benchmark, experiment_type))
        result_file_addr = Path(experiment_directory, "results", "addr_ila_results.vcd".format(
            benchmark, experiment_type))
        return result_file_gap.exists() and result_file_addr.exists()

    def extract_results(self, experiment_type, experiment_directory, addr_values_to_find):
        gap_vcd_file = parse_vcd(self.get_vcd_file_name(experiment_directory, "gap"))
        addr_vcd_file = parse_vcd(self.get_vcd_file_name(experiment_directory, "addr"))

        probes_to_extract = ["probe2", "probe3"]
        if "cc" in experiment_type:
            probes_to_extract = ["probe3", "probe4"]

        start_vcd_file = parse_vcd(self.get_vcd_file_name(experiment_directory, "start"))
        start_addr_time = self.get_addr_time(start_vcd_file, addr_values_to_find[0], 0, "cc" in experiment_type,
                                             "k_top/system_ila_2/inst/probe2_1[31:0]",
                                             "k_top/system_ila_2/inst/probe4_1[31:0]"
                                             )
        start_time = self.get_start_time_from_addr_time(start_addr_time, start_vcd_file,
                                                        "k_top/system_ila_2/inst/probe1_1",
                                                        "k_top/system_ila_2/inst/probe0_1",
                                                        "k_top/system_ila_2/inst/probe3_1[31:0]"
                                                        )

        try:
            number_memory_requests = len(
                [x['tv'] for x in gap_vcd_file.values() if probes_to_extract[1] in x['nets'][0]["name"]][0])
            if number_memory_requests == 0:
                return [[0, 0, 0, 0, start_time[0]]]
        except KeyError:
            return [[0, 0, 0, 0, start_time[0]]]

        extracted_gap_values = [x['tv'] for x in gap_vcd_file.values() if probes_to_extract[0] in x['nets'][0]["name"]][0]
        parsed_gap_values = {x[0]: int(x[1], base=2) for x in extracted_gap_values}
        extracted_gap_counter_values = [x['tv'] for x in gap_vcd_file.values() if probes_to_extract[1] in
                                        x['nets'][0]["name"]][0]
        parsed_gap_counter_values = {x[0]: int(x[1], base=2) for x in extracted_gap_counter_values}


        extracted_addr_values = [x['tv'] for x in addr_vcd_file.values() if probes_to_extract[0] in x['nets'][0]["name"]][0]
        extracted_counter_values = [x['tv'] for x in addr_vcd_file.values() if probes_to_extract[1] in x['nets'][0]["name"]][0]
        if "cc" in experiment_type:
            extracted_addr_values = [(i, x[1]) for i, x in enumerate(extracted_addr_values[1:])]
            extracted_counter_values = [(i, x[1]) for i, x in enumerate(extracted_counter_values[1:])]
        parsed_addr_values = {x[0]: hex(int(x[1], base=2)) for x in extracted_addr_values}
        parsed_counter_values = {x[0]: int(x[1], base=2) for x in extracted_counter_values}

        results = []
        previous_found_request = 0
        previous_addr_found = 0
        for request_number in range(0, number_memory_requests):
            try:
                results.append((parsed_gap_values[request_number], parsed_gap_counter_values[request_number],
                                parsed_addr_values[request_number], parsed_counter_values[request_number]))
                previous_found_request = request_number
                previous_addr_found = request_number
            except KeyError:
                try:
                    results.append((parsed_gap_values[previous_found_request], parsed_gap_counter_values[request_number],
                                    parsed_addr_values[request_number], parsed_counter_values[request_number]))
                    previous_addr_found = request_number
                except KeyError:
                    results.append((parsed_gap_values[previous_found_request], parsed_gap_counter_values[request_number],
                                    parsed_addr_values[previous_addr_found], parsed_counter_values[request_number]))

        return [[*x, start_time[0]] for x in results]

