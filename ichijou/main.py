import sys
import os

from pathlib import Path

from ichijou.compiler_interface import CompilerInterface


class Ichijou(object):

    compiler_interface = CompilerInterface(
        Path("/opt/riscv/bin")
    )

    def run_experiment(self, benchmark_path, temporary_file_location, debug):
        # Compile the benchmark
        self.compile_benchmark(benchmark_path, temporary_file_location, debug)
        # Generate the MEM File for the benchmark
        # Open up Vivado with the correct design // Open the VLAB
        # Generate the Bitstream if it doesn't exist
        # Run updatemem to program the MEM file into the bitstrea
        # Upload the design to the VLAB
        # Take any measurements from the ILA that are necessary (timings etc.)
        # Process the output into graphs etc.
        return 0

    def compile_benchmark(self, benchmark_path, temporary_file_location, debug):
        # Create a Boot File
        boot_file_location = self.compiler_interface.create_boot_program(temporary_file_location, "ff00")
        # Create Linker Script
        linker_file_location = self.compiler_interface.create_linker_file(temporary_file_location, 2**16, 2**16,
                                                                          0x4000)
        # Run compile option
        compiled_executable = self.compiler_interface.compile_benchmark(
            benchmark_path, linker_file_location, boot_file_location, temporary_file_location, "test.o"
        )
        # Clean up the temporary files
        if not debug:
            filelist = [f for f in os.listdir(temporary_file_location) if f != compiled_executable]
            for f in filelist:
                os.remove(os.path.join(temporary_file_location, f))
        # Return the address of the ELF file generated
        return compiled_executable


if __name__ == "__main__":
    system = Ichijou()
    system.run_experiment(Path(sys.argv[1]), sys.argv[2], True)
