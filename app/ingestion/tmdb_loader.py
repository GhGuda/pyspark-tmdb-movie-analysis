from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType,
    BooleanType,
    ArrayType
)
import os


def _tmdb_schema() -> StructType:
    """
    Defines the schema for TMDB movie data.

    Explicit schemas are mandatory in production Spark jobs
    to avoid silent data corruption and schema drift.
    """
    return StructType([
        StructField("id", IntegerType(), False),
        StructField("title", StringType(), True),
        StructField("release_date", StringType(), True),
        StructField("budget", DoubleType(), True),
        StructField("revenue", DoubleType(), True),
        StructField("runtime", IntegerType(), True),
        StructField("vote_average", DoubleType(), True),
        StructField("vote_count", IntegerType(), True),
        StructField("original_language", StringType(), True),
        StructField("adult", BooleanType(), True),
        StructField("genres", ArrayType(StringType()), True),
    ])


def load_tmdb_movies(spark: SparkSession) -> DataFrame:
    """
    Loads TMDB movie data into a Spark DataFrame.

    This function performs ingestion only:
    - Reads raw JSON files
    - Applies schema
    - Returns Spark DataFrame
    """

    raw_path = os.getenv(
        "TMDB_RAW_PATH",
        "/opt/app/data/raw_data"
    )

    df = (
        spark.read
        .schema(_tmdb_schema())
        .json(raw_path)
    )

    return df
