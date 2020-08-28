import os
import subprocess
import re

from pathlib import Path

from ichijou.template_interface import TemplateInterface


class MEMFileGenerator(object):

    @staticmethod
    def generate_new_mem_file(contents, temp_dir, benchmark_name, data_offset, experiment_type):
        temp_dir = Path(temp_dir, "mem")
        os.makedirs(temp_dir, exist_ok=True)
        file_paths = []
        for c, _ in enumerate(contents["data"]):
            contents["data"][c] = (contents["data"][c][0] - data_offset // 4, contents["data"][c][1])
        for memory_name, file_contents in contents.items():
            output_file_name = Path(temp_dir, "{}_{}_{}_memory.mem".format(
                benchmark_name, experiment_type, memory_name))
            if not os.path.isfile(output_file_name):
                results = ["@0"]
                counter = 0
                if file_contents:
                    for i in range(0, file_contents[0][0]):
                        results.append("FFFFFFFF")
                    counter = file_contents[0][0]
                    for pair in file_contents:
                        if pair[0] != counter:
                            for i in range(counter, pair[0]):
                                results.append("FFFFFFFF")
                            counter = pair[0]
                        for instruction in pair[1]:
                            results.append(instruction)
                            counter += 1
                with open(output_file_name, "w") as mem_fp:
                    for file_line in results:
                        mem_fp.write(file_line + '\n')
            else:
                with open(output_file_name, "r") as mem_fp:
                    results = mem_fp.readlines()
            file_paths.append((sum([1 for x in results if x[0] != "@"]), output_file_name))
        return file_paths


class VivadoInterface(object):

    base_project_name = "kuuga_experiment"
    mem_file_instruction_limit = 32768/32
    experiment_type_mapper = {
        "nc": ("kuuga_top_no_cache.v", "kuuga_nc", "kuuga_no_cache"),
        "sc_dm": ("kuuga_top_simple_cache_dm.v", "kuuga_sc_dm", "kuuga_simple_cache_dm"),
        "sc_nway": ("kuuga_top_simple_cache_nway.v", "kuuga_sc_nway", "kuuga_simple_cache_nway"),
        "cc_dm": ("kuuga_top_complex_cache_dm.v", "kuuga_cc_dm", "kuuga_complex_cache_dm"),
        "cc_nway": ("kuuga_top_complex_cache_nway.v", "kuuga_cc_nway", "kuuga_complex_cache_nway"),
        "nc_mg": ("kuuga_top_no_cache.v", "kuuga_nc_mg", "kuuga_no_cache_mg"),
        "sc_dm_mg": ("kuuga_top_simple_cache_dm.v", "kuuga_sc_dm_mg", "kuuga_simple_cache_dm_mg"),
        "sc_nway_mg": ("kuuga_top_simple_cache_nway.v", "kuuga_sc_nway_mg", "kuuga_simple_cache_nway_mg"),
        "cc_dm_mg": ("kuuga_top_complex_cache_dm.v", "kuuga_cc_dm_mg", "kuuga_complex_cache_dm_mg"),
        "cc_nway_mg": ("kuuga_top_complex_cache_nway.v", "kuuga_cc_nway_mg", "kuuga_complex_cache_nway_mg")
    }

    def setup_experiment(self, mem_file_paths, temporary_path, benchmark, experiment_type, trigger_values):
        experiment_names = self.experiment_type_mapper[experiment_type]
        original_top_level = \
            (Path(temporary_path, "..", "..", "..", "Kuuga", "rtl", experiment_names[0]), experiment_names[1],
             experiment_names[2])
        temporary_files_path = Path(temporary_path, "vivado_files")
        os.makedirs(temporary_files_path, exist_ok=True)
        # Check if the top-level file needs re-writing
        if not Path(temporary_files_path, "top_level.v").exists():
            top_level = (self.create_new_top_level(
                temporary_files_path, Path(temporary_path, "..", "..", "templates"), original_top_level[1],
                mem_file_paths, original_top_level[2]), original_top_level[1], original_top_level[2])
        else:
            top_level = (Path(temporary_files_path, "top_level.v"), original_top_level[1], original_top_level[2])
        results_folder_path = Path(temporary_path, "results")
        results_files_path = Path(results_folder_path, "{0}_{1}_ila_results.vcd".format(benchmark, experiment_type))
        os.makedirs(results_folder_path, exist_ok=True)
        if not Path(temporary_files_path, "setup_experiment_environment.tcl").exists():
            tcl_setup_script_path = self.create_tcl_script(temporary_files_path,
                                                           Path(temporary_path, "..", "..", "templates"),
                                                           mem_file_paths, benchmark, top_level, trigger_values,
                                                           experiment_type, results_files_path,
                                                           "experiment_mg_tcl.template" if ("mg" in experiment_type)
                                                           else "experiment_tcl.template")
        else:
            tcl_setup_script_path = Path(temporary_files_path, "setup_experiment_environment.tcl")
        subprocess.run(
            "{0} {1}".format(
                Path(temporary_path, "..", "..", "scripts", "sh", "run_vivado.sh").absolute(), tcl_setup_script_path),
            shell=True
        )
        return

    @staticmethod
    def create_new_top_level(temporary_files_path, templates_path, top_level_module, mem_file_paths, system_under_test):
        return TemplateInterface.create_file_from_template(
            Path(templates_path, "top_level.template"),
            temporary_files_path,
            "top_level.v",
            {
                "top_level_module": top_level_module,
                "instruction_memory_file": mem_file_paths[0][1].name,
                "data_memory_file": mem_file_paths[1][1].name,
                "system_under_test": system_under_test
            }
        )

    def create_tcl_script(self, temporary_files_path, templates_path, mem_file_paths, benchmark_name, top_level,
                          trigger_values, experiment_type, output_file_location, template_name="experiment_tcl.template"
                          ):
        project_location = Path(temporary_files_path, "..", "vivado_project")
        return TemplateInterface.create_file_from_template(
            Path(templates_path, template_name),
            temporary_files_path,
            "setup_experiment_environment.tcl",
            {
                "top_level": top_level,
                "instruction_memory_file": mem_file_paths[0][1].name,
                "data_memory_file": mem_file_paths[1][1].name,
                "benchmark": benchmark_name,
                "project_location_join_syntax": re.sub("{}".format(os.sep), " ",
                                                       str(project_location.relative_to(temporary_files_path))),
                "project_name": "{}_{}_{}".format(self.base_project_name, benchmark_name, experiment_type),
                "kuuga_location_join_syntax": re.sub(
                    "{}".format(os.sep), " ", str(Path(temporary_files_path, "..", "..", "..", "..",
                                                       "Kuuga").relative_to(temporary_files_path))),
                "trigger_values": trigger_values,
                "output_file_location": output_file_location.absolute(),
                "experiment_type": experiment_type
            }
        )
