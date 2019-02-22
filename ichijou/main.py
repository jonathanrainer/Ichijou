import sys

from pathlib import Path


class Ichijou(object):

    def run_experiment(self, benchmark_path):
        # Compile the benchmark
        self.compile_benchmark(benchmark_path)
        # Generate the MEM File for the benchmark
        # Open up Vivado with the correct design // Open the VLAB
        # Generate the Bitstream if it doesn't exist
        # Run updatemem to program the MEM file into the bitstrea
        # Upload the design to the VLAB
        # Take any measurements from the ILA that are necessary (timings etc.)
        # Process the output into graphs etc.
        return 0

    def compile_benchmark(self, benchmark_path):
        # Create a Boot File & Linker Script
        # Run compile option
        # Return the address of the ELF file generated
        return


if __name__ == "__main__":
    system = Ichijou()
    system.run_experiment(Path(sys.argv[1]))
