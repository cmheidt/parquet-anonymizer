import polars as pl

from parquet_anonymizer.config import Config
from parquet_anonymizer.field_types.field_type_factory import FieldTypeFactory
from parquet_anonymizer.user.user_callback import UserCallback


def anonymize_dataframe(
    config: Config, df: pl.DataFrame, user_callback: UserCallback = None
) -> pl.DataFrame:
    for column_name in config.columns_to_anonymize:
        if column_name not in df.columns:
            raise ValueError(f"{column_name} not found in dataframe.")

        type_config_dict = config.columns_to_anonymize[column_name]
        field_type = FieldTypeFactory.get_type(type_config_dict)

        if field_type is not None:
            df = df.with_columns(
                pl.when(pl.col(column_name).is_not_null() & (pl.col(column_name) != ""))
                .then(
                    pl.col(column_name).map_elements(
                        lambda x: field_type.generate_obfuscated_value(
                            config.secret_key, x, user_callback
                        )
                    )
                )
                .otherwise(pl.col(column_name))
                .alias(column_name)
            )

    return df


def anonymize_csv(
    config: Config, in_filename: str, out_filename: str, user_callback: UserCallback = None
):
    df = pl.read_csv(in_filename, separator=config.delimiter)
    df = anonymize_dataframe(config, df, user_callback)
    df.write_csv(out_filename, separator=config.delimiter)


def anonymize_parquet(
    config: Config, in_filename: str, out_filename: str, user_callback: UserCallback = None
):
    df = pl.read_parquet(in_filename)
    df = anonymize_dataframe(config, df, user_callback)
    df.write_parquet(out_filename)


def anonymize_xlsx(
    config: Config, in_filename: str, out_filename: str, user_callback: UserCallback = None
):
    df = pl.read_excel(in_filename)
    df = anonymize_dataframe(config, df, user_callback)
    df.write_excel(out_filename)
