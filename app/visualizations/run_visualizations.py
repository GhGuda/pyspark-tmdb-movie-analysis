import pandas as pd
from app.visualizations.generate_plots import (
    plot_revenue_vs_budget,
    plot_roi_distribution_by_genre,
    plot_popularity_vs_rating,
    plot_yearly_box_office_trends,
    plot_franchise_vs_standalone
)

def run():
    movies_df = pd.read_parquet("data/processed/movies_enriched")
    franchise_df = pd.read_parquet(
        "data/processed/analytics/franchise_vs_standalone"
    )

    plot_revenue_vs_budget(movies_df)
    plot_roi_distribution_by_genre(movies_df)
    plot_popularity_vs_rating(movies_df)
    plot_yearly_box_office_trends(movies_df)
    plot_franchise_vs_standalone(franchise_df)


if __name__ == "__main__":
    run()
