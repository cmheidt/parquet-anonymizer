import logging
import click
import os

from parquet_anonymizer.config import Config
from parquet_anonymizer.config_generator import generate_yaml_config
from parquet_anonymizer.anonymizer import anonymize_csv, anonymize_parquet, anonymize_xlsx
from parquet_anonymizer.util import keygen, DEFAULT_KEY_FILE


@click.command()
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--has-header", is_flag=True, help="Indicates whether the data file contains a header row."
)
@click.option(
    "--delimiter",
    default=",",
    help='Only needed for CSV files. The delimiter used in the data file (e.g., ",", "\t").',
)
def generate_config(file, has_header, delimiter):
    """Generates a YAML configuration file based on the provided data file."""
    generate_yaml_config(file, has_header, delimiter)


@click.command()
@click.option(
    "--in-file",
    type=click.Path(exists=True),
    help="Path to the file to be anonymized.",
    required=True,
)
@click.option("--out-file", type=click.Path(), help="Path to the output file.")
@click.option(
    "--config-file",
    type=click.Path(exists=True),
    help="Path to the configuration file.",
    required=True,
)
@click.option(
    "--delimiter", help="Delimiter used in the data file. For CSV files. Defaults to ','."
)
@click.option(
    "--key-file",
    type=click.Path(),
    help="Path to the key file to be used for anonymization. If not provided, a random key "
    + "will be generated.",
)
def anonymize_file(in_file, out_file, config_file, delimiter, key_file=None):
    """Anonymizes a file using the provided configuration file."""
    for path in [in_file, config_file]:
        if not os.path.isfile(path):
            logging.error(f"No such file: {path}")
            return
    if out_file is None:
        out_file = (
            in_file.replace(".csv", "_anonymized.csv")
            .replace(".parquet", "_anonymized.parquet")
            .replace(".xlsx", "_anonymized.xlsx")
        )
    if key_file is None:
        key_dir = os.path.dirname(in_file) + "/"
        key_file = key_dir + DEFAULT_KEY_FILE
        keygen(key_file)
        logging.warning(f"No key file provided. Generating a random key and saving to {key_file}.")
    config = Config(yaml_path=config_file, key_file_path=key_file, delimiter=delimiter)
    if in_file.endswith(".csv"):
        anonymize_csv(config, in_file, out_file)
    elif in_file.endswith(".parquet"):
        anonymize_parquet(config, in_file, out_file)
    elif in_file.endswith(".xlsx"):
        anonymize_xlsx(config, in_file, out_file)
    else:
        logging.error("Unsupported file format. Supported formats are: csv, parquet, xlsx.")


@click.group()
def cli():
    """Anonymizer CLI for CSV, Parquet, and Excel files."""


if __name__ == "__main__":
    cli.add_command(generate_config)
    cli.add_command(anonymize_file)
    cli()
