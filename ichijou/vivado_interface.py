import os
import subprocess
import re

from pathlib import Path

from ichijou.template_interface import TemplateInterface


class MEMFileGenerator(object):

    @staticmethod
    def generate_new_mem_file(contents, temp_dir, benchmark_name, data_offset):
        temp_dir = Path(temp_dir, "mem")
        os.makedirs(temp_dir, exist_ok=True)
        file_paths = []
        for c, _ in enumerate(contents["data"]):
            contents["data"][c] = (contents["data"][c][0] - data_offset // 4, contents["data"][c][1])
        for memory_name, file_contents in contents.items():
            output_file_name = Path(temp_dir, "{}_{}_memory.mem".format(benchmark_name, memory_name))
            if not os.path.isfile(output_file_name):
                results = ["@0"]
                counter = 0
                if file_contents:
                    for i in range(1, file_contents[0][0]):
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

    base_project_name = "KuugaTest"
    mem_file_instruction_limit = 32768/32

    def setup_experiment(self, mem_file_paths, temporary_path, benchmark):
        # Generate necessary files (top-level design, tcl script to run the experiment)
        top_levels = [
            (Path(temporary_path, "..", "..", "..", "Kuuga", "rtl", "kuuga_top_no_cache.v"), "kuuga_nc",
             "kuuga_no_cache"),
            (Path(temporary_path, "..", "..", "..", "Kuuga", "rtl", "kuuga_top_simple_cache.v"), "kuuga_sc",
             "kuuga_simple_cache"),
            (Path(temporary_path, "..", "..", "..", "Kuuga", "rtl", "kuuga_top_complex_cache.v"), "kuuga_cc",
             "kuuga_complex_cache")
        ]
        temporary_files_path = Path(temporary_path, "vivado_files")
        os.makedirs(temporary_files_path, exist_ok=True)
        # Check if the top-level file needs re-writing
        if self.check_for_resynth(mem_file_paths):
            for index, old_top_level in enumerate(top_levels):
                top_levels[index] = (self.create_new_top_level(
                    temporary_files_path, Path(temporary_path, "..", "..", "templates"), old_top_level[1],
                    mem_file_paths, old_top_level[2]), old_top_level[1], old_top_level[2])
        tcl_setup_script_path = self.create_tcl_setup_script(
            temporary_files_path,  Path(temporary_path, "..", "..", "templates"), mem_file_paths,
            benchmark, self.check_for_resynth(mem_file_paths),  top_levels)
        # Call the shell script passing in the correct arguments
        os.makedirs(Path(temporary_path, "output"), exist_ok=True)
        subprocess.run(
            "{0} {1}".format(
                Path(temporary_path, "..", "..", "scripts", "sh", "run_vivado.sh").absolute(), tcl_setup_script_path),
            shell=True
        )
        return

    def check_for_resynth(self, mem_file_paths):
        for pair in mem_file_paths:
            if pair[0] > self.mem_file_instruction_limit:
                return True
        return False

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

    def create_tcl_setup_script(self, temporary_files_path, templates_path, mem_file_paths, benchmark_name,
                          resynth, top_levels):
        project_location = Path(temporary_files_path, "..", "vivado_project") \
            if resynth else Path(temporary_files_path, "..", "..", "common")
        return TemplateInterface.create_file_from_template(
            Path(templates_path, "project_tcl.template"),
            temporary_files_path,
            "setup_experiment_environment.tcl",
            {
                "top_levels": top_levels,
                "instruction_memory_file": mem_file_paths[0][1].name,
                "data_memory_file": mem_file_paths[1][1].name,
                "benchmark": benchmark_name,
                "project_location_join_syntax": re.sub("{}".format(os.sep), " ",
                                                       str(project_location.relative_to(temporary_files_path))),
                "project_name": "{}_{}".format(self.base_project_name, benchmark_name) if resynth
                else self.base_project_name,
                "resynth": "1" if resynth else "0",
                "kuuga_location_join_syntax": re.sub(
                    "{}".format(os.sep), " ", str(Path(temporary_files_path, "..", "..", "..", "..",
                                                       "Kuuga").relative_to(temporary_files_path))
                )
            }
        )
