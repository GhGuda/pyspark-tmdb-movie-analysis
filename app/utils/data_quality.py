from pyspark.sql import DataFrame
from pyspark.sql.functions import col
from typing import List
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
