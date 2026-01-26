from pyspark.sql import DataFrame
from pyspark.sql.functions import col, when


def add_budget_revenue_musd(df: DataFrame) -> DataFrame:
    """
    Adds budget and revenue in millions of USD.

    Standardizing units early avoids repeated conversions
    and inconsistent KPI definitions downstream.
    """
    return (
        df
        .withColumn("budget_musd", col("budget") / 1_000_000)
        .withColumn("revenue_musd", col("revenue") / 1_000_000)
    )


def add_profit(df: DataFrame) -> DataFrame:
    """
    Adds profit KPI: revenue minus budget.
    """
    return df.withColumn(
        "profit_musd",
        col("revenue_musd") - col("budget_musd")
    )


def add_roi(df: DataFrame) -> DataFrame:
    """
    Adds ROI (Return on Investment).

    ROI = revenue / budget

    Null-safe and division-by-zero safe.
    """
    return df.withColumn(
        "roi",
        when(
            col("budget_musd") > 0,
            col("revenue_musd") / col("budget_musd")
        ).otherwise(None)
    )
