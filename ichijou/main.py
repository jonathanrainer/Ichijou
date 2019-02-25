import sys
import os

from pathlib import Path

from ichijou.compiler_interface import CompilerInterface
from ichijou.vivado_interface import MEMFileGenerator
from ichijou.elf_file_interface import ELFFileInterface


class Ichijou(object):

    compiler_interface = CompilerInterface(
        Path("/opt/riscv/bin")
    )
    mem_file_generator = MEMFileGenerator()
    elf_file_interface = ELFFileInterface()

    def run_experiment(self, benchmark_path, temporary_file_location, debug):
        # Compile the benchmark
        data_offset = 0x10000
        executable_file = self.compile_benchmark(benchmark_path, temporary_file_location, data_offset, debug)
        # Generate the MEM File for the benchmark
        mem_file_paths = self.mem_file_generator.generate_new_mem_file(
            self.elf_file_interface.extract_mem_file_elements(executable_file), temporary_file_location,
            benchmark_path.stem, data_offset)
        # Open up Vivado with the correct design // Open the VLAB
        print("Hello World")
        # Generate the Bitstream if it doesn't exist
        # Run updatemem to program the MEM file into the bitstrea
        # Upload the design to the VLAB
        # Take any measurements from the ILA that are necessary (timings etc.)
        # Process the output into graphs etc.
        return 0

    def compile_benchmark(self, benchmark_path, temporary_file_location, data_offset, debug):
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
        # Clean up the temporary files
        if not debug:
            file_list = [f for f in os.listdir(temporary_file_location) if f != compiled_executable.name]
            for f in file_list:
                os.remove(os.path.join(temporary_file_location, f))
        # Return the address of the ELF file generated
        return compiled_executable


if __name__ == "__main__":
    system = Ichijou()
    system.run_experiment(Path(sys.argv[1]), sys.argv[2], False)
