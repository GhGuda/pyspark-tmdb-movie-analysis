import os
from app.spark_job.session import get_spark_session
from app.utils.logging import get_logger
from app.ingestion.tmdb_loader import load_tmdb_movies
from app.transformations.enrichments import (
    add_franchise_type,
    clean_movies, 
    convert_column_datatypes, 
    drop_irrelevant_columns, 
    extract_cast_and_crew, 
    extracting_name_from_columns, 
    reorder_columns, 
    replacing_unrealistic_values
)
from app.transformations.kpis import (
    add_profit,
    add_roi
)
from app.analytics.rankings import (
    compare_franchise_vs_standalone_performance,
    most_successful_franchises,
    most_successful_directors,
    rank_movies,
    best_rated_sci_fi_movies,
    uma_thurman_tarantino_movies,
)
from app.utils.data_quality import check_not_empty, check_no_nulls
from pyspark.sql.functions import col




def run() -> None:
    spark = get_spark_session()
    logger = get_logger("tmdb-pipeline")
    
    silver_path = os.getenv(
        "TMDB_SILVER_PATH",
        "/opt/app/data/processed/movies_enriched"
    )
    
    gold_path = os.getenv(
        "TMDB_GOLD_PATH",
        "/opt/app/data/processed/analytics"
    )
    

    try:
        logger.info("TMDB pipeline started")

        # --------------------------------------------------
        # STAGE 1: Load raw data (Bronze)
        # --------------------------------------------------
        logger.info("Lodading TMDB raw data")
        
        raw_df = load_tmdb_movies(spark)
        
        raw_df.printSchema()
        raw_df.show(5, truncate=False)
        raw_df.select("id").show(5)
        raw_df.count()
        check_not_empty(raw_df, "raw_movies")

        # --------------------------------------------------
        # STAGE 2: Enrichment (Silver)
        # --------------------------------------------------
        logger.info("Applying Enrichment")
        
        enriched_df = (
            raw_df
            .transform(drop_irrelevant_columns)
            .transform(extracting_name_from_columns)
            .transform(add_franchise_type)
            .transform(convert_column_datatypes)
            .transform(replacing_unrealistic_values)
            .transform(clean_movies)
            .transform(extract_cast_and_crew)
            .transform(reorder_columns)
        )

        check_not_empty(enriched_df, "movies_enriched")
        check_no_nulls(enriched_df, ["id", "title"], "movies_enriched")

        # Persist Silver
        logger.info("Saving processed data")
        
        enriched_df.write.mode("overwrite").parquet(silver_path)

        # --------------------------------------------------
        # STAGE 3: KPI computation (Gold)
        # --------------------------------------------------
        logger.info("Applying KPI transformations")
        kpi_df = (
            enriched_df
            .transform(add_profit)
            .transform(add_roi)
        )
        kpi_df.write.mode("overwrite").parquet(
            f"{gold_path}/movies_with_kpis"
        )
        check_no_nulls(
            kpi_df,
            ["budget_musd", "revenue_musd"],
            "movies_with_kpis"
        )

        # --------------------------------------------------
        # STAGE 3A: Rankings
        # --------------------------------------------------
        top_roi_df = rank_movies(
            kpi_df.filter(col("budget_musd") >= 10),
            metric="roi",
            n=10,
            kpi_label="Highest ROI (Budget ≥ 10M)"
        )

        # --------------------------------------------------
        # STAGE 3B: Aggregations
        # --------------------------------------------------
        franchise_vs_standalone_df = compare_franchise_vs_standalone_performance(kpi_df)
        franchise_df = most_successful_franchises(kpi_df)
        director_df = most_successful_directors(kpi_df)

        # Persist Gold outputs
        top_roi_df.write.mode("overwrite").parquet(f"{gold_path}/top_movies_by_roi")
        franchise_vs_standalone_df.write.mode("overwrite").parquet(
            f"{gold_path}/franchise_vs_standalone"
        )
        franchise_df.write.mode("overwrite").parquet(
            f"{gold_path}/most_successful_franchises"
        )
        director_df.write.mode("overwrite").parquet(
            f"{gold_path}/most_successful_directors"
        )

        logger.info("TMDB Spark pipeline completed successfully")

    except Exception:
        logger.exception("TMDB pipeline failed")
        raise

    finally:
        spark.stop()



if __name__ == "__main__":
    run()