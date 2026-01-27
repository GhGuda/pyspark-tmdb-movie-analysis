import os
import pandas as pd
from app.visualizations.generate_plots import (
    plot_revenue_vs_budget,
    plot_roi_distribution_by_genre,
    plot_popularity_vs_rating,
    plot_yearly_box_office_trends,
    plot_franchise_vs_standalone
)
from app.utils.logging import get_logger


logger = get_logger("visualizations")

def run():
    logger.info("Starting TMDB visualizations")

    movies_path = "data/processed/movies_enriched"
    kpi_path = "data/processed/analytics/movies_with_kpis"
    franchise_path = "data/processed/analytics/franchise_vs_standalone"

    ran_any = False

    # ------------------------------
    # Silver-based plots
    # ------------------------------
    if os.path.exists(movies_path):
        logger.info(f"Found movies dataset at {movies_path}")
        movies_df = pd.read_parquet(movies_path)

        logger.info("Generating Revenue vs Budget plot")
        plot_revenue_vs_budget(movies_df)

        logger.info("Generating Popularity vs Rating plot")
        plot_popularity_vs_rating(movies_df)

        logger.info("Generating Yearly Box Office Trends plot")
        plot_yearly_box_office_trends(movies_df)

        ran_any = True
    else:
        logger.warning(f"Movies dataset not found at {movies_path}")

    # ------------------------------
    # Gold KPI plots
    # ------------------------------
    if os.path.exists(kpi_path):
        logger.info(f"Found KPI dataset at {kpi_path}")
        kpi_df = pd.read_parquet(kpi_path)

        logger.info("Generating ROI Distribution by Genre plot")
        plot_roi_distribution_by_genre(kpi_df)

        ran_any = True
    else:
        logger.warning(f"KPI dataset not found at {kpi_path}")

    # ------------------------------
    # Gold analytics plots
    # ------------------------------
    if os.path.exists(franchise_path):
        logger.info(f"Found franchise analytics dataset at {franchise_path}")
        franchise_df = pd.read_parquet(franchise_path)

        logger.info("Generating Franchise vs Standalone plot")
        plot_franchise_vs_standalone(franchise_df)

        ran_any = True
    else:
        logger.warning(f"Franchise analytics dataset not found at {franchise_path}")

    if not ran_any:
        logger.error("No data available for visualizations")

    logger.info("TMDB visualizations completed")

if __name__ == "__main__":
    run()