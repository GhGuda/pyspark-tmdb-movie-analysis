from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lit, when, avg, count, expr, sum as _sum


def rank_movies(
    df: DataFrame,
    metric: str,
    top: bool = True,
    n: int = 10,
    kpi_label: str | None = None
) -> DataFrame:
    """
    Rank movies by a metric.
    """

    ordered_df = df.orderBy(
        col(metric).desc() if top else col(metric).asc()
    )

    ranked_df = ordered_df.limit(n)

    if kpi_label:
        ranked_df = ranked_df.withColumn("kpi", lit(kpi_label))

    return ranked_df



def best_rated_sci_fi_movies(df: DataFrame) -> DataFrame:
    """
    Retrieve best-rated Sci-Fi Action movies starring Bruce Willis.
    """
    return (
        df
        .filter(col("genres").rlike("(?i)Science Fiction"))
        .filter(col("genres").rlike("(?i)Action"))
        .filter(col("cast").rlike("(?i)Bruce Willis"))
        .orderBy(col("vote_average").desc())
    )
    
    
def uma_thurman_tarantino_movies(df: DataFrame) -> DataFrame:
    """
    Retrieve movies featuring Uma Thurman and directed by Quentin Tarantino.
    """
    return (
        df
        .filter(col("cast").rlike("(?i)Uma Thurman"))
        .filter(col("director").rlike("(?i)Quentin Tarantino"))
        .orderBy(col("runtime").asc())
    )
    


def compare_franchise_vs_standalone_performance(df: DataFrame) -> DataFrame:
    """
    Compare performance of franchise movies vs standalone movies.
    """
    df = df.withColumn(
        "franchise_type",
        when(col("belongs_to_collection").isNotNull(), "Franchise")
        .otherwise("Standalone")
    )

    return (
        df
        .groupBy("franchise_type")
        .agg(
            avg("revenue_musd").alias("mean_revenue"),
            expr("percentile_approx(roi, 0.5)").alias("median_roi"),
            avg("budget_musd").alias("mean_budget"),
            avg("popularity").alias("mean_popularity"),
            avg("vote_average").alias("mean_rating")
        )
        .orderBy(col("mean_revenue").desc())
    )
    
    

def most_successful_franchises(df: DataFrame) -> DataFrame:
    """
    Identify the most successful movie franchises based on average revenue.
    """
    return (
        df
        .filter(col("belongs_to_collection").isNotNull())
        .groupBy("belongs_to_collection")
        .agg(
            count("id").alias("total_movies"),
            _sum("budget_musd").alias("total_budget"),
            avg("budget_musd").alias("mean_budget"),
            _sum("revenue_musd").alias("total_revenue"),
            avg("revenue_musd").alias("mean_revenue"),
            avg("vote_average").alias("mean_rating")
        )
        .orderBy(col("mean_revenue").desc())
    )
    
    
    
def most_successful_directors(df: DataFrame) -> DataFrame:
    """
    Identify the most successful directors based on total revenue.
    """
    return (
        df
        .filter(col("director").isNotNull())
        .groupBy("director")
        .agg(
            count("id").alias("total_movies"),
            _sum("revenue_musd").alias("total_revenue"),
            avg("vote_average").alias("mean_rating")
        )
        .orderBy(col("total_revenue").desc())
    )


