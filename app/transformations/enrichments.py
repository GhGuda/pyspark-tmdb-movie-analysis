from pyspark.sql import DataFrame
from pyspark.sql.functions import col, when, expr, to_date, size


        
def drop_irrelevant_columns(movies_df: DataFrame) -> DataFrame:
    """
        Drops columns that are not relevant for analysis.
        This transformation helps in reducing the DataFrame size
        and focusing on the most pertinent information for
        TMDB movie analytics.
    """
    drop_columns = [
        "adult",
        "imdb_id",
        "original_title",
        "video",
        "homepage"
    ]

    existing = [c for c in drop_columns if c in movies_df.columns]
    return movies_df.drop(*existing)



def extracting_name_from_columns(movies_df: DataFrame) -> DataFrame:
    """
        Extracts the 'name' field from nested structures in specific columns.
        This transformation simplifies the DataFrame by converting complex
        nested fields into flat string representations, making it easier to analyze
        and visualize the data.
    """
    if "belongs_to_collection" in movies_df.columns:
        movies_df = movies_df.withColumn(
            "belongs_to_collection",
            col("belongs_to_collection.name")
        )
    mappings = {
        "genres": "name",
        "production_countries": "name",
        "production_companies": "name",
        "spoken_languages": "name"
    }

    for column, field in mappings.items():
        if column in movies_df.columns:
            movies_df = movies_df.withColumn(
                column,
                expr(f"concat_ws('|', transform({column}, x -> x.{field}))")
            )

    return movies_df



def check_anomalies(movies_df: DataFrame) -> dict:
    """
        Checks for anomalies in specific columns by counting occurrences
        of unique values. This function helps identify potential data
        quality issues or unexpected distributions in the dataset.
    """
    columns = [
        "genres",
        "spoken_languages",
        "production_companies",
        "production_countries",
        "belongs_to_collection"
    ]

    results = {}
    for c in columns:
        if c in movies_df.columns:
            results[c] = (
                movies_df
                .groupBy(c)
                .count()
                .orderBy("count", ascending=False)
            )

    return results



def convert_column_datatypes(movies_df: DataFrame) -> DataFrame:
    """
        Converts column data types to appropriate formats for analysis.
        Ensures numeric columns are of type Double and date columns
        are in Date format.
    """
    numeric_cols = [
        "budget",
        "revenue",
        "popularity",
        "id",
        "vote_count",
        "vote_average",
        "runtime"
    ]

    for c in numeric_cols:
        if c in movies_df.columns:
            movies_df = movies_df.withColumn(c, col(c).cast("double"))

    if "release_date" in movies_df.columns:
        movies_df = movies_df.withColumn(
            "release_date",
            to_date("release_date")
        )

    return movies_df



def replacing_unrealistic_values(movies_df: DataFrame) -> DataFrame:
    """
        Replaces unrealistic zero values in specific columns with nulls.
        This transformation helps in cleaning the dataset by removing
        potentially erroneous data points that could skew analysis results.
    """
    for c in ["budget", "revenue", "runtime"]:
        if c in movies_df.columns:
            movies_df = movies_df.withColumn(
                c,
                when(col(c) == 0, None).otherwise(col(c))
            )

    movies_df = (
        movies_df
        .withColumn("budget_musd", col("budget") / 1_000_000)
        .withColumn("revenue_musd", col("revenue") / 1_000_000)
    )

    if "vote_count" in movies_df.columns and "vote_average" in movies_df.columns:
        movies_df = movies_df.withColumn(
            "vote_average",
            when(col("vote_count") == 0, None).otherwise(col("vote_average"))
        )

    placeholders = ["No Data", "", "N/A", "na", "null"]
    for c in ["overview", "tagline"]:
        if c in movies_df.columns:
            movies_df = movies_df.withColumn(
                c,
                when(col(c).isin(placeholders), None).otherwise(col(c))
            )

    return movies_df



def clean_movies(movies_df: DataFrame) -> DataFrame:
    """
        Cleans the movies DataFrame by removing duplicates,
        rows with nulls in critical columns, and rows with
        insufficient non-null data.
    """
    movies_df = (
        movies_df
        .dropDuplicates(["id", "title"])
        .dropna(subset=["id", "title"])
    )

    # Keep rows with at least 10 non-null columns
    non_null_expr = " + ".join(
        [f"CASE WHEN {c} IS NOT NULL THEN 1 ELSE 0 END" for c in movies_df.columns]
    )
    movies_df = movies_df.filter(expr(f"{non_null_expr} >= 10"))

    if "status" in movies_df.columns:
        movies_df = (
            movies_df
            .filter(expr("status = 'Released'"))
            .drop("status")
        )

    return movies_df



def extract_cast_and_crew(movies_df: DataFrame) -> DataFrame:
    """
        Extracts cast and crew information from the credits column.
    """
    if "credits" not in movies_df.columns:
        return movies_df

    movies_df = movies_df.withColumn(
        "cast",
        expr("concat_ws('|', transform(credits.cast, x -> x.name))")
    )

    movies_df = movies_df.withColumn(
        "cast_size",
        size(expr("credits.cast"))
    )

    movies_df = movies_df.withColumn(
        "director",
        expr(
            "concat_ws('|', transform(filter(credits.crew, x -> x.job = 'Director'), x -> x.name))"
        )
    )

    movies_df = movies_df.withColumn(
        "crew_size",
        size(expr("credits.crew"))
    )

    return movies_df



def add_franchise_type(movies_df: DataFrame) -> DataFrame:
    return movies_df.withColumn(
        "franchise_type",
        when(col("belongs_to_collection").isNotNull(), "Franchise")
        .otherwise("Standalone")
    )



def reorder_columns(movies_df: DataFrame) -> DataFrame:
    """
        Reorders columns in a predefined logical sequence.
        This transformation enhances readability and consistency
        of the DataFrame for analysis and reporting.
    """
    ordered_columns = [
        "id", "title", "tagline", "release_date", "genres",
        "belongs_to_collection", "original_language",
        "budget_musd", "revenue_musd",
        "production_companies", "production_countries",
        "vote_count", "vote_average", "popularity",
        "runtime", "overview", "spoken_languages",
        "poster_path", "cast", "cast_size",
        "director", "crew_size"
    ]

    cols_present = [c for c in ordered_columns if c in movies_df.columns]
    return movies_df.select(*cols_present)