from . import BaseFieldType
from .decorators import apply_formatting_options
from .decorators.apply_user_callback import apply_user_callback


class FileName(BaseFieldType):
    @apply_formatting_options
    @apply_user_callback
    def generate_obfuscated_value(self, key, value, *args, **kwargs):
        self.seed_faker(key, value)
        return self.faker.file_name()
