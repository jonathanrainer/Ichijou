import sys
import os
import shutil

from pathlib import Path

from ichijou.compiler_interface import CompilerInterface
from ichijou.vivado_interface import MEMFileGenerator, VivadoInterface
from ichijou.elf_file_interface import ELFFileInterface


class Ichijou(object):

    compiler_interface = CompilerInterface(
        Path("/opt/riscv/bin")
    )
    elf_file_interface = ELFFileInterface()
    vivado_interface = VivadoInterface()

    def run_experiment(self, benchmark_path, experiments_directory, debug):
        # Compile the benchmark
        experiment_directory = Path(experiments_directory, benchmark_path.stem)
        os.makedirs(experiment_directory, exist_ok=True)
        data_offset = 0x10000
        executable_file = self.compile_benchmark(benchmark_path, experiment_directory, data_offset)
        # Generate the MEM File for the benchmark
        mem_file_paths = MEMFileGenerator.generate_new_mem_file(
            self.elf_file_interface.extract_mem_file_elements(executable_file), experiment_directory,
            benchmark_path.stem, data_offset)
        # Open up Vivado with the correct design
        self.vivado_interface.open_vivado_with_script(mem_file_paths, experiment_directory, benchmark_path.stem)
        #####################################################################
        # Take any measurements from the ILA that are necessary (timings etc.)
        # Process the output into graphs etc.
        return 0

    def compile_benchmark(self, benchmark_path, temporary_file_location, data_offset):
        temporary_file_location = Path(temporary_file_location, "executable")
        output_file_name = "{0}.elf".format(benchmark_path.stem)
        output_path = Path(temporary_file_location, output_file_name)
        os.makedirs(temporary_file_location, exist_ok=True)
        if not os.path.isfile(output_path):
            # Create a Boot File
            boot_file_location = self.compiler_interface.create_boot_program(temporary_file_location, "ff00")
            # Create Linker Script
            linker_file_location = self.compiler_interface.create_linker_file(temporary_file_location, 2**16, 2**16,
                                                                              0x4000, data_offset)
            # Run compile option
            compiled_executable = self.compiler_interface.compile_benchmark(
                benchmark_path, linker_file_location, boot_file_location, temporary_file_location,
                "{0}.elf".format(benchmark_path.stem)
            )
        else:
            compiled_executable = output_path
        return compiled_executable


if __name__ == "__main__":
    system = Ichijou()
    if len(sys.argv) == 3:
        system.run_experiment(Path(sys.argv[1]), sys.argv[2], False)
    elif len(sys.argv) == 4:
        system.run_experiment(Path(sys.argv[1]), sys.argv[2], True)
