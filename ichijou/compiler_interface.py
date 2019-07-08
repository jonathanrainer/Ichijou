import subprocess

from pathlib import Path

from ichijou.template_interface import TemplateInterface


class CompilerInterface(object):

    riscv_binary_prefix = ""
    boot_file_template = Path("~", "Documents", "PhD", "Ichijou", "templates", "boot.template").expanduser()
    boot_file_repeat_template = Path("~", "Documents", "PhD", "Ichijou", "templates",
                                     "boot_repeat.template").expanduser()
    linker_file_template = Path("~", "Documents", "PhD", "Ichijou", "templates", "link.template").expanduser()

    def __init__(self, riscv_binary_prefix):
        self.riscv_binary_prefix = riscv_binary_prefix

    def create_linker_file(self, temporary_path, instruction_memory_size, data_memory_size, stack_size, data_offset):
        return TemplateInterface.create_file_from_template(
            self.linker_file_template, temporary_path, "link.ld",
            {
                "program_start": 0x200,
                "instruction_mem_size": instruction_memory_size,
                "data_start": data_offset,
                "data_mem_size": data_memory_size,
                "stack_size": stack_size,
            }
        )

    def create_boot_program(self, temporary_path, stack_pointer_location, experiment_type):
        return TemplateInterface.create_file_from_template(
                self.boot_file_repeat_template if "cc" in experiment_type else self.boot_file_template,
                temporary_path, "boot.S",
                {
                    "stack_pointer_loc": stack_pointer_location
                }
            )

    def compile_benchmark(self, benchmark_path, linker_file_path, boot_file_path, temporary_path, output_file_name):
        output_file = Path(temporary_path, output_file_name)
        #  Compile it
        subprocess.run(
            "{0}/riscv32-unknown-elf-gcc -nostartfiles {1} {2} -T {3} -o {4}".format(
                self.riscv_binary_prefix,
                boot_file_path,
                benchmark_path,
                linker_file_path,
                str(output_file.absolute())
            ), shell=True
        )
        return output_file


