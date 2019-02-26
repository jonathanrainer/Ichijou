import os

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
            counter = file_contents[0][0]
            results = ["@" + f"{counter:0{8}x}"]
            for pair in file_contents:
                if pair[0] != counter:
                    new_addr = pair[0]
                    results.append("@" + f"{new_addr:0{8}x}")
                for instruction in pair[1]:
                    results.append(instruction)
                    counter += 1
            file_path = Path(temp_dir, "{}_{}_memory.mem".format(benchmark_name, memory_name))
            with open(file_path, "w") as mem_fp:
                for file_line in results:
                    mem_fp.write(file_line + '\n')
            file_paths.append((sum([1 for x in results if x[0] != "@"]), file_path))
        return file_paths


class VivadoInterface(object):

    project_name = "KuugaTest"
    mem_file_instruction_limit = 32768/32

    def open_vivado_with_script(self, mem_file_paths, temporary_path, benchmark):
        # Generate necessary files (top-level design, tcl script to run the experiment)
        top_level = None
        top_level_module = "kuuga_top"
        temporary_files_path = Path(temporary_path, "vivado_files")
        os.makedirs(temporary_files_path, exist_ok=True)
        # Check if the top-level file needs re-writing
        if self.check_for_resynth(mem_file_paths):
            top_level = self.create_new_top_level(temporary_files_path, Path(temporary_path, "..", "templates"),
                                                  top_level_module, mem_file_paths)
        print("Hello World")
        self.create_tcl_script(temporary_files_path, Path(temporary_path, "..", "templates"), mem_file_paths,
                               benchmark, top_level is not None,  top_level, top_level_module
                               )
        # Call the shell script passing in the correct arguments
        return

    def check_for_resynth(self, mem_file_paths):
        for pair in mem_file_paths:
            if pair[0] > self.mem_file_instruction_limit:
                return True
        return False

    @staticmethod
    def create_new_top_level(temporary_files_path, templates_path, top_level_module, mem_file_paths):
        return TemplateInterface.create_file_from_template(
            Path(templates_path, "top_level.template"),
            temporary_files_path,
            "top_level.v",
            {
                "top_level_module": top_level_module,
                "instruction_memory_file": mem_file_paths[0][1].name,
                "data_memory_file": mem_file_paths[1][1].name
            }
        )

    def create_tcl_script(self, temporary_files_path, templates_path, mem_file_paths, benchmark_name,
                          resynth, top_level_file=None, top_level_module=None):
        return TemplateInterface.create_file_from_template(
            Path(templates_path, "project_tcl.template"),
            temporary_files_path,
            "run_experiment.tcl",
            {
                "top_level_module": top_level_module,
                "instruction_memory_file": mem_file_paths[0][1].name,
                "data_memory_file": mem_file_paths[1][1].name,
                "benchmark": benchmark_name,
                "project_name": self.project_name,
                "resynth": 1 if resynth else 0,
                "top_level_file": top_level_file

            }
        )
