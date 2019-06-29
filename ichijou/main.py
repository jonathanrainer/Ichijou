import sys
import os

from pathlib import Path

from ichijou.compiler_interface import CompilerInterface
from ichijou.vivado_interface import MEMFileGenerator, VivadoInterface
from ichijou.elf_file_interface import ELFFileInterface
from ichijou.data_capture_interface import DataCaptureInterface
from ichijou.vcd_interface import VCDInterface


class Ichijou(object):

    compiler_interface = CompilerInterface(
        Path("/opt/riscv/bin")
    )
    elf_file_interface = ELFFileInterface()
    vivado_interface = VivadoInterface()
    vcd_interface = VCDInterface()
    data_capture_interface = None

    def __init__(self, results_file):
        self.data_capture_interface = DataCaptureInterface(results_file)

    def run_experiment(self, benchmark_path, experiments_directory, experiment_type):
        # Compile the benchmark
        experiment_directory = Path(experiments_directory, "{}_{}".format(benchmark_path.stem, experiment_type))
        os.makedirs(experiment_directory, exist_ok=True)
        data_offset = 0x10000
        if not self.data_capture_interface.result_present(benchmark_path.stem, experiment_type):
            executable_file = self.compile_benchmark(benchmark_path, experiment_directory, data_offset,
                                                     experiment_type)
            if not self.vcd_interface.does_raw_result_exist(benchmark_path.stem, experiment_type, experiment_directory):
                # Generate the MEM File for the benchmark
                mem_file_path = MEMFileGenerator.generate_new_mem_file(
                    self.elf_file_interface.extract_mem_file_elements(executable_file), experiment_directory,
                    benchmark_path.stem, data_offset, experiment_type)
                # Open up Vivado with the correct design
                self.vivado_interface.setup_experiment(
                    mem_file_path, experiment_directory, benchmark_path.stem,
                    experiment_type,
                self.elf_file_interface.extract_trigger_values(executable_file, experiment_type))
            # Take any measurements from the ILA that are necessary (timings etc.)
            results = self.vcd_interface.extract_results(
                benchmark_path.stem, experiment_type, experiment_directory,
                self.elf_file_interface.extract_addr_values_to_find(executable_file))
            self.data_capture_interface.store_result(benchmark_path.stem, experiment_type, results)
        return 0

    def compile_benchmark(self, benchmark_path, temporary_file_location, data_offset, experiment_type):
        temporary_file_location = Path(temporary_file_location, "executable")
        output_file_name = "{0}_{1}.elf".format(benchmark_path.stem, experiment_type)
        output_path = Path(temporary_file_location, output_file_name)
        os.makedirs(temporary_file_location, exist_ok=True)
        if not os.path.isfile(output_path):
            # Create a Boot File
            boot_file_location = self.compiler_interface.create_boot_program(temporary_file_location, "ff00",
                                                                             experiment_type)
            # Create Linker Script
            linker_file_location = self.compiler_interface.create_linker_file(temporary_file_location, 2**16, 2**16,
                                                                              0x4000, data_offset)
            # Run compile option
            compiled_executable = self.compiler_interface.compile_benchmark(
                benchmark_path, linker_file_location, boot_file_location, temporary_file_location, output_file_name
            )
        else:
            compiled_executable = output_path
        return compiled_executable


if __name__ == "__main__":
    system = Ichijou(sys.argv[4])
    system.run_experiment(Path(sys.argv[1]), sys.argv[2], sys.argv[3])
