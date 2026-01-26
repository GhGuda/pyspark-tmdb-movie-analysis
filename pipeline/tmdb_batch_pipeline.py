import os
from app.spark_job.session import get_spark_session
from app.utils.logging import get_logger
from app.ingestion.tmdb_loader import load_tmdb_movies
from app.transformations.enrichments import Tranformation
from app.transformations.kpis import (
    add_budget_revenue_musd,
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

    try:
        logger.info("TMDB pipeline started")

        # --------------------------------------------------
        # STAGE 1: Load raw data (Bronze)
        # --------------------------------------------------
        raw_df = load_tmdb_movies(spark)
        check_not_empty(raw_df, "raw_movies")

        # --------------------------------------------------
        # STAGE 2: Enrichment (Silver)
        # --------------------------------------------------
        transformer = Tranformation(raw_df)
        enriched_df = transformer.drop_irrelevant_columns()
        enriched_df = transformer.extracting_name_from_columns()
        enriched_df = transformer.check_anomalies()
        enriched_df = transformer.convert_column_datatypes()
        enriched_df = transformer.replacing_unrealistic_values()
        enriched_df = transformer.clean_movies()
        enriched_df = transformer.extract_cast_and_crew()
        enriched_df = transformer.reorder_columns()

        check_not_empty(enriched_df, "movies_enriched")
        check_no_nulls(enriched_df, ["id", "title"], "movies_enriched")

        # Persist Silver
        silver_path = os.getenv(
            "TMDB_SILVER_PATH",
            "/opt/app/data/processed/movies_enriched"
        )
        enriched_df.write.mode("overwrite").parquet(silver_path)

        # --------------------------------------------------
        # STAGE 3: KPI computation (Gold)
        # --------------------------------------------------
        kpi_df = (
            enriched_df
            .transform(add_budget_revenue_musd)
            .transform(add_profit)
            .transform(add_roi)
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
        gold_path = os.getenv(
            "TMDB_GOLD_PATH",
            "/opt/app/data/processed/analytics"
        )

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
