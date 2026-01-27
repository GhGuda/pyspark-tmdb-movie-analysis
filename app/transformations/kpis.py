from pyspark.sql import DataFrame
from pyspark.sql.functions import col, when

def add_profit(df: DataFrame) -> DataFrame:
    """
    Adds profit KPI: revenue minus budget.
    """
    return df.withColumn(
        "profit",
        col("revenue_musd") - col("budget_musd")
    )


def add_roi(df: DataFrame) -> DataFrame:
    """
    Adds ROI (Return on Investment).

    ROI = (Revenue - Budget) / Budget_musd

    Null-safe and division-by-zero safe.
    """
    return df.withColumn(
        "roi",
        when(
            col("budget_musd") > 0,
            col("profit") / col("budget_musd")
        )
    )
