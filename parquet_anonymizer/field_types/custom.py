from . import BaseFieldType
from .decorators.apply_user_callback import apply_user_callback
from .decorators.text_formatter import apply_formatting_options


class Custom(BaseFieldType):
    def __init__(self, type_config_dict):
        super().__init__(type_config_dict)
        format_string = type_config_dict.get("format")
        if not format_string or not isinstance(format_string, str):
            raise ValueError("Custom field types must have a format defined of type string")
        self.format = type_config_dict["format"]

    @apply_formatting_options
    @apply_user_callback
    def generate_obfuscated_value(self, key, value, *args, **kwargs):
        self.seed_faker(key, value)
        retval = self.faker.bothify(self.format)
        # check if format_string contains only #, if so, return a number
        if all([c == "#" for c in self.format]):
            return int(retval)
        return retval
