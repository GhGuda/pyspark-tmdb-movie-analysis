from pyspark.sql import SparkSession
import os


def get_spark_session() -> SparkSession:
    """
    Creates and returns a SparkSession for TMDB batch analytics.

    This function centralizes all Spark-related configuration
    and guarantees consistent behavior across environments
    (local, Docker, CI, production).
    """

    app_name = os.getenv("SPARK_APP_NAME", "tmdb-spark-batch")

    spark = (
        SparkSession.builder
        .appName(app_name)
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "200")
        .getOrCreate()
    )

    return spark
