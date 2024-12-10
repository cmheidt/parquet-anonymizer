from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap


class Config:
    def __init__(self, yaml_path=None, key_file_path=None, **kwargs):
        self.config_dict = CommentedMap()
        for keyword in kwargs:
            self.config_dict[keyword] = kwargs[keyword]
        if yaml_path is not None:
            with open(yaml_path) as config_file:
                yaml = YAML(typ="safe")
                self.config_dict = yaml.load(config_file)
        else:
            self.config_dict["columns_to_anonymize"] = {}
        if key_file_path is not None:
            with open(key_file_path) as key_file:
                self.secret_key = key_file.read().strip()

    @property
    def columns_to_anonymize(self):
        return self.config_dict.get("columns_to_anonymize")

    @property
    def delimiter(self):
        return self.config_dict.get("delimiter")

    def add_column_config(self, column_name, column_config_dict):
        self.config_dict["columns_to_anonymize"][column_name] = column_config_dict

    def save_config(self, save_name=None):
        if save_name is None:
            from datetime import date

            save_name = date.today().strftime("%Y-%m-%d_generated_config.yml")
        with open(save_name, "w") as save_file:
            yaml = YAML()
            yaml.default_flow_style = False
            yaml.dump(self.config_dict, save_file)


class SecretKeyNotSetException(Exception):
    pass
