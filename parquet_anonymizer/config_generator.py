import os
import logging
import polars as pl
import dateutil.parser as date_parser

from .config import Config

# TODO: optimize


def generate_yaml_config(data_file, has_header, delimiter, enableOptions=True):
    """
    Generates a YAML configuration file based on the provided data file.

    Args:
        data_file (str): Path to the data file to be used for generating the configuration.
        has_header (bool): Indicates whether the data file contains a header row.
        delimiter (str): The delimiter used in the data file (e.g., ',', '\t').
        enableOptions (bool, optional): Flag to enable or disable additional options.
        Defaults to True.

    Returns:
        None

    The function builds a data dictionary from the provided data file, determines the best
    configuration for each column, and saves the generated configuration to a YAML file. The
    generated configuration file is saved in the same directory as the data file with a name based
    on the data file's name.
    """
    data_dict = build_data_dictionary(data_file, has_header, delimiter)
    new_config = Config(delimiter=delimiter)
    for column in data_dict:
        column_config = get_best_column_config_for_column(
            data_dict[column], enableOptions=enableOptions
        )
        if column_config is None:
            continue
        new_config.add_column_config(column, column_config)
    if os.path.dirname(data_file) != "":
        data_file_path = os.path.dirname(data_file) + "/"
        file_base_name = os.path.splitext(os.path.basename(data_file))[0]
        config_file_name = "{}generated-{}-config.yml".format(data_file_path, file_base_name)
    else:
        config_file_name = "generated-{}-config.yml".format(data_file)
    get_logger().info(f"Saving generated config file to: {config_file_name}")
    new_config.save_config(save_name=config_file_name)


def get_logger():
    return logging.getLogger("config_generator")


def build_data_dictionary(data_file, has_header=True, delimiter=","):
    """
    Builds a dictionary where the keys are the columns in the file, and the values are lists of
    that column's values.

    Args:
        data_file (str): The path to the data file.
        has_header (bool, optional): Whether the file has a header row. Defaults to True.
        delimiter (str, optional): The delimiter used in the file. Defaults to ",".

    Returns:
        dict: A dictionary with column names as keys and lists of column values as values.

    Raises:
        ValueError: If the file format is unsupported.
    """
    file_extension = data_file.split(".")[-1].lower()

    if file_extension == "csv":
        df = pl.read_csv(data_file, has_header=has_header, separator=delimiter)
    elif file_extension in ["xlsx", "xls"]:
        df = pl.read_excel(data_file, read_csv_options={"has_header": has_header})
    elif file_extension == "parquet":
        df = pl.read_parquet(data_file)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

    if not has_header:
        df.columns = [str(i) for i in range(len(df.columns))]

    return {col: df[col].to_list() for col in df.columns}


def get_best_column_config_for_column(column_values, enableOptions=True):
    """
    Determines the best configuration for a given column based on its values.

    This function evaluates the column values and returns the most appropriate
    configuration. It first checks if the column contains date/time values and
    returns the corresponding configuration if found. If not, and if the
    `enableOptions` flag is set to True, it checks if the column has fewer than
    five hundred unique values and returns an options-based configuration. If
    neither condition is met, it returns a default custom configuration.

    Args:
        column_values (list): A list of values in the column to be evaluated.
        enableOptions (bool, optional): A flag to enable or disable the options
                                        configuration check. Defaults to True.

    Returns:
        dict: The configuration for the column, or None if the column is empty.
    """
    if len(column_values) == 0:
        return
    column_config = get_date_time_config_if_dates_found(column_values)
    if column_config:
        return column_config
    if enableOptions:
        column_config = get_options_config_if_fewer_than_five_hundred(column_values)
    if column_config:
        return column_config
    return get_default_custom_column_config(column_values)


def get_date_time_config_if_dates_found(column_values):
    """
    If the values in the column look like dates, return a datetime column configuration
    in the range of all the dates found in the column.
    :param column_values: list: A list of column values
    :return: dict: A dictionary containing the type of configuration and the date range
    """
    sample_value: str = column_values.pop(0)
    while sample_value is None and len(column_values) > 0:
        sample_value = column_values.pop(0)
    if sample_value is None:
        return
    match = get_matched_date(sample_value)
    if match is not None:
        column_values.append(sample_value)
        min_date = None
        max_date = None
        for value in column_values:
            matched_date = get_matched_date(value)
            if matched_date is not None:
                if min_date is None or matched_date < min_date:
                    min_date = matched_date
                if max_date is None or matched_date > max_date:
                    max_date = matched_date
        return {
            "type": "datetime",
            "format": "%Y-%m-%d",
            "range_start_date": min_date.strftime("%Y-%m-%d"),
            "range_end_date": max_date.strftime("%Y-%m-%d"),
        }


def get_matched_date(value):
    """
    Parses a date string and returns a datetime object if the string is a valid date.

    :param value (str): The date string to be parsed.
    :return datetime.datetime or None: A datetime object if the string is a valid date,
                                   None if the string is too short or cannot be parsed.
    """
    if len(str(value)) < 6:
        return
    try:
        return date_parser.parse(str(value))
    except ValueError:
        return
    except OverflowError:
        get_logger().debug("Got overflow error trying to match %s", value)


def get_options_config_if_fewer_than_five_hundred(column_values):
    """
    If there are fewer than 500 unique values for a column, return an Options configuration dict
    :param column_values (list): A list of column values
    :return: dict: A dictionary containing the type of configuration and the unique values
    """
    unique_dict = {}
    for value in column_values:
        unique_dict[value] = True
    uniques = list(unique_dict.keys())
    if len(unique_dict.values()) < 500:
        return {"type": "options", "options": uniques}


def get_default_custom_column_config(column_values):
    """
    Generate a default custom column configuration based on the sample values provided.

    Takes a list of column values, extracts the first non-None value, and generates a
    format string where alphabetic characters are replaced with '?', numeric characters are
    replaced with '#', and other characters remain unchanged. If all values are None, a default
    format string "????" is returned.

    :param column_values (list): A list of column values from which to derive the format string.
    :return: dict: A dictionary containing the type of configuration and the generated format string
    """
    sample_value: str = str(column_values.pop(0))
    while sample_value is None and len(column_values) > 0:
        sample_value = str(column_values.pop(0))
    if sample_value is None:
        format_string = "????"
    else:
        format_string = ""
        for char in sample_value:
            if char.isalpha():
                format_string += "?"
            elif char.isnumeric():
                format_string += "#"
            else:
                format_string += char
    return {"type": "custom", "format": format_string}
