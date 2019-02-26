from jinja2 import Template
from pathlib import Path


class TemplateInterface(object):

    @staticmethod
    def create_file_from_template(template_file_path, temporary_path, output_file_name, params):
        with open(str(template_file_path)) as boot_file_pointer:
            template = Template(boot_file_pointer.read())
        output_path = Path(temporary_path, output_file_name)
        with open(str(output_path), "w") as output_file_pointer:
            output_file_pointer.write(template.render(**params))
        return output_path
