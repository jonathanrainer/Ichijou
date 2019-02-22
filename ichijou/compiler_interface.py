from pathlib import Path
from jinja2 import Template


class CompilerInterface(object):

    riscv_binary_prefix = ""
    boot_file_template = Path("~", "Documents", "PhD", "Ichijou", "templates", "boot.template").expanduser()

    def __init__(self, riscv_binary_prefix):
        self.riscv_binary_prefix = riscv_binary_prefix

    def create_linker_file(self):
        return

    def create_boot_program(self, temporary_path, stack_pointer_location):
        return self.create_file_from_template(
            self.boot_file_template, temporary_path, "boot.S",
            {"stack_pointer_loc": stack_pointer_location})

    @staticmethod
    def create_file_from_template(template_file_path, temporary_path, output_file_name, params):
        with open(str(template_file_path)) as boot_file_pointer:
            template = Template(boot_file_pointer.read())
        output_path = Path(temporary_path, output_file_name)
        with open(str(output_path), "w") as output_file_pointer:
            output_file_pointer.write(template.render(**params))
        return output_path



