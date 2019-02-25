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
