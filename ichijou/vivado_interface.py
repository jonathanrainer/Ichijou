from pathlib import Path


class MEMFileGenerator(object):

    @staticmethod
    def generate_new_mem_file(contents, temp_dir, benchmark_name, data_offset):
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
            file_paths.append(file_path)
        return file_paths
