from app.utils.logging import get_logger
from app.spark_job.session import get_spark_session
from app.ingestion.tmdb_loader import load_tmdb_movies
from app.transformations.kpis import (
    add_profit,
    add_roi
)





def main() -> None:
    """
    Entry point for TMDB Spark batch analytics job.
    """

    # 1. Start Spark
    spark = get_spark_session()
    logger = get_logger("tmdb-batch")
    logger.info("Starting TMDB Spark batch job")

    try:
        # 2. Load raw TMDB data
        logger.info("Loading TMDB raw data")
        movies_df = load_tmdb_movies(spark)

        movies_df.printSchema()
        movies_df.show(5, truncate=False)
        movies_df.select("id").show(5)
        movies_df.count()

        movies_df = movies_df.filter(col("id").isNotNull())
        movies_df = movies_df.filter(col("title").isNotNull())

        
        check_not_empty(movies_df, "movies_df")
        check_no_nulls(
            movies_df,
            columns=["id", "title"],
            df_name="movies_df"
        )
        
        movies_df = (
            movies_df
            .withColumn("budget", col("budget").cast("double"))
            .withColumn("revenue", col("revenue").cast("double"))
        )


        # 3. Apply KPI transformations
        logger.info("Applying KPI transformations")
        movies_df = add_budget_revenue_musd(movies_df)
        movies_df = add_profit(movies_df)
        movies_df = add_roi(movies_df)
        
        check_no_nulls(
            movies_df,
            columns=["budget_musd", "revenue_musd"],
            df_name="movies_df_with_kpis"
        )


        # 4. Analytics: top movies by ROI
        logger.info("Running analytics rankings")
        top_roi_df = top_movies_by_metric(
            movies_df,
            metric="roi",
            top_n=10
        )


        # 5. Write outputs
        logger.info("Writing output datasets")
        
        output_path = os.getenv(
            "TMDB_OUTPUT_PATH",
            "/opt/app/data/processed"
        )

        (
            movies_df
            .write
            .mode("overwrite")
            .parquet(f"{output_path}/movies_enriched")
        )

        (
            top_roi_df
            .write
            .mode("overwrite")
            .parquet(f"{output_path}/top_movies_by_roi")
        )
    
        logger.info("TMDB Spark batch job completed successfully")


    finally:
        # 6. Stop Spark cleanly
        spark.stop()


if __name__ == "__main__":
    main()
