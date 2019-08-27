from elftools.elf.elffile import ELFFile


class ELFFileInterface(object):

    def extract_mem_file_elements(self, elf_file):
        with open(str(elf_file.absolute()), 'rb') as elf_fp:
            elf_file = ELFFile(elf_fp)  # type: ELFFile
            instruction_memory_contents = self.extract_sections(
                [".reset", ".illegal_instruction", ".text"], elf_file
            )
            data_memory_contents = self.extract_sections(
                [".rodata", ".bss", ".data"], elf_file
            )
            result = {
                "instruction": sorted(instruction_memory_contents, key=lambda a: a[0]),
                "data": sorted(data_memory_contents, key=lambda a: a[0])
            }
        return result

    @staticmethod
    def extract_sections(searches, elf_file):
        results = []
        for section_name in searches:
            try:
                raw_bytes = bytearray(elf_file.get_section_by_name(section_name).data())
            except AttributeError:
                continue
            raw_bytes.reverse()
            hex_string = raw_bytes.hex()
            instructions = [hex_string[i:i + 8] for i in range(0, len(hex_string), 8)]
            instructions.reverse()
            results.append(
                (elf_file.get_section_by_name(section_name).header["sh_addr"] // 4,
                 instructions)
            )
        return results

    def extract_trigger_values(self, elf_file, experiment_type):
        with open(str(elf_file.absolute()), 'rb') as elf_fp:
            elf_file = ELFFile(elf_fp)
            text_section = self.extract_sections([".text"], elf_file)[0]
            starting_index = elf_file.get_section_by_name(".symtab").get_symbol_by_name("_boot")[0].entry.st_value // 4\
                             - text_section[0]
            counter_values = [
                f"{((text_section[0] + i) * 4):0{4}x}" for i, x in enumerate( text_section[1][starting_index:],
                                                                      start= starting_index)
                if int(x[-2:], base=16) in [0xe3, 0x63, 0xef, 0x6f, 0xe7, 0x67]
                ]
        if "cc" in experiment_type:
            return [counter_values[0], counter_values[1], counter_values[-1]]
        else:
            return [counter_values[0], counter_values[0], counter_values[-1]]

    @staticmethod
    def extract_addr_values_to_find(elf_file):
        with open(str(elf_file.absolute()), 'rb') as elf_fp:
            elf_file = ELFFile(elf_fp)
            main_addr = hex(elf_file.get_section_by_name(".symtab").get_symbol_by_name("main")[0].entry.st_value)
            trap_addr = hex(elf_file.get_section_by_name(".symtab").get_symbol_by_name("_trap")[0].entry.st_value)
        return [main_addr, trap_addr]
