import logging
import xxhash
import faker


class BaseFieldType:
    def __init__(self, type_config_dict):
        self.type_config_dict = type_config_dict
        self.faker = FakerSingleton()

    @staticmethod
    def generate_seed(key, value):
        # cast value to str if not str
        if not isinstance(value, str):
            value = str(value)
        combination = key + value
        value = xxhash.xxh64(combination.encode()).hexdigest()
        return value

    @staticmethod
    def get_logger():
        return logging.getLogger("config_field")

    def seed_faker(self, key, field_value):
        seed = BaseFieldType.generate_seed(key, field_value)
        faker.Faker.seed(seed)

    def generate_obfuscated_value(self, key, value, *args, **kwargs):
        raise NotImplementedError


class FakerSingleton:
    """
    Using the singleton pattern since we only need the one instance of Faker,
    and instantiating Faker is expensive (~0.02 seconds)
    """

    class __FakerSingleton:
        def __init__(self, *args, **kwargs):
            self.faker = faker.Faker(*args, **kwargs)

    instance = None

    def __init__(self, *args, **kwargs):
        if not FakerSingleton.instance:
            FakerSingleton.instance = FakerSingleton.__FakerSingleton(*args, **kwargs)

    def __getattr__(self, item):
        return getattr(self.instance.faker, item)
