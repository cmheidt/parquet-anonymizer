from parquet_anonymizer.field_types import BaseFieldType
from .decorators import apply_formatting_options
from .decorators.apply_user_callback import apply_user_callback


class County(BaseFieldType):
    @apply_formatting_options
    @apply_user_callback
    def generate_obfuscated_value(self, key, value, *args, **kwargs):
        self.seed_faker(key, value)
        return '{} County'.format(self.faker.last_name())
