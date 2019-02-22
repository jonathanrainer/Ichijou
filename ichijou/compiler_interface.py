class CompilerInterface(object):

    riscv_binary_prefix = ""

    def __init__(self, riscv_binary_prefix):
        self.riscv_binary_prefix = riscv_binary_prefix

    def create_linker_file(self):
        return

    def create_boot_program(self):
        return

