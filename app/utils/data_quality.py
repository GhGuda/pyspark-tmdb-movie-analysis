from typing import Iterable, List, Sequence

from pyspark.sql import DataFrame
from pyspark.sql.functions import col
from pyspark.sql.types import StructType
from app.utils.logging import get_logger


logger = get_logger("data-quality")


def check_not_empty(df: DataFrame, df_name: str) -> None:
    """
    Ensures DataFrame is not empty.
    """
    count = df.count()
    if count == 0:
        raise ValueError(f"Data quality check failed: {df_name} is empty")

    logger.info(f"{df_name} passed non-empty check ({count} records)")


def check_no_nulls(df: DataFrame, columns: List[str], df_name: str) -> None:
    """
    Ensures specified columns do not contain nulls.
    """
    for column in columns:
        null_count = df.filter(col(column).isNull()).count()
        if null_count > 0:
            raise ValueError(
                f"Data quality check failed: {column} has {null_count} null values"
            )

        logger.info(f"{df_name}.{column} passed null check")


def check_columns_present(
    df: DataFrame,
    columns: Sequence[str],
    df_name: str,
) -> None:
    """
    Ensures required columns exist in the DataFrame.
    """
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(
            f"Data quality check failed: {df_name} missing columns {missing}"
        )

    logger.info(f"{df_name} passed required columns check")


def check_schema(
    df: DataFrame,
    expected_schema: StructType,
    df_name: str,
) -> None:
    """
    Ensures the DataFrame schema matches the expected schema.
    """
    if not isinstance(expected_schema, StructType):
        raise TypeError("expected_schema must be a StructType")

    expected = {field.name: field.dataType.simpleString() for field in expected_schema}
    actual = {field.name: field.dataType.simpleString() for field in df.schema}

    missing = [name for name in expected.keys() if name not in actual]
    mismatched = [
        name
        for name, dtype in expected.items()
        if name in actual and actual[name] != dtype
    ]

    if missing or mismatched:
        raise ValueError(
            "Data quality check failed: "
            f"{df_name} schema mismatch. Missing={missing}, "
            f"TypeMismatch={mismatched}"
        )

    logger.info(f"{df_name} passed schema check")


def check_non_negative(
    df: DataFrame,
    columns: Iterable[str],
    df_name: str,
) -> None:
    """
    Ensures numeric columns have no negative values.
    """
    for column in columns:
        if column not in df.columns:
            continue
        negative_count = df.filter(col(column) < 0).count()
        if negative_count > 0:
            raise ValueError(
                f"Data quality check failed: {df_name}.{column} "
                f"has {negative_count} negative values"
            )

        logger.info(f"{df_name}.{column} passed non-negative check")


def check_range(
    df: DataFrame,
    column: str,
    df_name: str,
    min_value: float | None = None,
    max_value: float | None = None,
) -> None:
    """
    Ensures a numeric column is within the given range.
    """
    if column not in df.columns:
        return

    invalid = None
    if min_value is not None:
        invalid = col(column) < min_value
    if max_value is not None:
        invalid = (invalid | (col(column) > max_value)) if invalid is not None else (col(column) > max_value)

    if invalid is None:
        return

    out_of_range_count = df.filter(col(column).isNotNull() & invalid).count()
    if out_of_range_count > 0:
        raise ValueError(
            f"Data quality check failed: {df_name}.{column} "
            f"has {out_of_range_count} values outside the range [{min_value}, {max_value}]"
        )

    logger.info(f"{df_name}.{column} passed range check")
