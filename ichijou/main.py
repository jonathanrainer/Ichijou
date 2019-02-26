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
    mem_file_generator = MEMFileGenerator()
    elf_file_interface = ELFFileInterface()
    vivado_interface = VivadoInterface()

    def run_experiment(self, benchmark_path, temporary_file_location, debug):
        # Compile the benchmark
        data_offset = 0x10000
        executable_file = self.compile_benchmark(benchmark_path, temporary_file_location, data_offset)
        # Generate the MEM File for the benchmark
        mem_file_paths = self.mem_file_generator.generate_new_mem_file(
            self.elf_file_interface.extract_mem_file_elements(executable_file), temporary_file_location,
            benchmark_path.stem, data_offset)
        # Open up Vivado with the correct design
        self.vivado_interface.open_vivado_with_script(mem_file_paths, temporary_file_location, benchmark_path.stem)
        if not debug:
            self.clean_temporary_files(temporary_file_location)
        #####################################################################
        # Take any measurements from the ILA that are necessary (timings etc.)
        # Process the output into graphs etc.
        return 0

    def compile_benchmark(self, benchmark_path, temporary_file_location, data_offset):
        temporary_file_location = Path(temporary_file_location, "executable")
        os.makedirs(temporary_file_location, exist_ok=True)
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
        return compiled_executable

    @staticmethod
    def clean_temporary_files(temporary_file_location):
        for the_file in os.listdir(temporary_file_location):
            file_path = os.path.join(temporary_file_location, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    system = Ichijou()
    if len(sys.argv) == 3:
        system.run_experiment(Path(sys.argv[1]), sys.argv[2], False)
    elif len(sys.argv) == 4:
        system.run_experiment(Path(sys.argv[1]), sys.argv[2], True)
