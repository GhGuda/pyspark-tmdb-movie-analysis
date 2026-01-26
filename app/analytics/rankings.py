from pyspark.sql import DataFrame
from pyspark.sql.window import Window
from pyspark.sql.functions import col, row_number


def top_movies_by_metric(
    df: DataFrame,
    metric: str,
    top_n: int = 10
) -> DataFrame:
    """
    Returns top N movies ranked by a given metric.

    Parameters:
    - metric: column name to rank by (e.g. 'roi', 'revenue_musd')
    - top_n: number of top records to return
    """

    window = Window.orderBy(col(metric).desc())

    return (
        df
        .withColumn("rank", row_number().over(window))
        .filter(col("rank") <= top_n)
    )


def bottom_movies_by_metric(
    df: DataFrame,
    metric: str,
    bottom_n: int = 10
) -> DataFrame:
    """
    Returns bottom N movies ranked by a given metric.
    """

    window = Window.orderBy(col(metric).asc())

    return (
        df
        .withColumn("rank", row_number().over(window))
        .filter(col("rank") <= bottom_n)
    )
