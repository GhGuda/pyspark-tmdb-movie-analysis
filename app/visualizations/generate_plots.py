import os
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_DIR = os.getenv(
    "TMDB_PLOTS_PATH",
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


def plot_revenue_vs_budget(df: pd.DataFrame):
    """
    Generates and saves a scatter plot of Revenue vs Budget.
    """
    plt.figure(figsize=(8, 6))

    plt.scatter(
        df["budget_musd"],
        df["revenue_musd"],
        alpha=0.5
    )

    plt.xlabel("Budget (Million USD)")
    plt.ylabel("Revenue (Million USD)")
    plt.title("Revenue vs Budget Trends")

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/revenue_vs_budget.png")
    plt.close()



def plot_roi_distribution_by_genre(df: pd.DataFrame):
    """
    Generates and saves a box plot of ROI distribution by genre.
    """
    exploded = (
        df[["genres", "roi"]]
        .dropna()
        .assign(genres=lambda x: x["genres"].str.split("|"))
        .explode("genres")
    )

    top_genres = (
        exploded["genres"]
        .value_counts()
        .head(8)
        .index
    )

    data = exploded[exploded["genres"].isin(top_genres)]

    plt.figure(figsize=(10, 6))
    data.boxplot(
        column="roi",
        by="genres",
        rot=45
    )

    plt.title("ROI Distribution by Genre")
    plt.suptitle("")
    plt.xlabel("Genre")
    plt.ylabel("ROI")

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/roi_distribution_by_genre.png")
    plt.close()



def plot_popularity_vs_rating(df: pd.DataFrame):
    """
    Generates and saves a scatter plot of Popularity vs Average Rating.
    """
    plt.figure(figsize=(8, 6))

    plt.scatter(
        df["popularity"],
        df["vote_average"],
        alpha=0.5
    )

    plt.xlabel("Popularity")
    plt.ylabel("Average Rating")
    plt.title("Popularity vs Rating")

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/popularity_vs_rating.png")
    plt.close()



def plot_yearly_box_office_trends(df: pd.DataFrame):
    """
    Generates and saves a line plot of yearly average box office revenue.
    """
    yearly = (
        df.dropna(subset=["release_date", "revenue_musd"])
        .assign(year=lambda x: x["release_date"].dt.year)
        .groupby("year", as_index=False)["revenue_musd"]
        .mean()
    )

    plt.figure(figsize=(10, 6))
    plt.plot(yearly["year"], yearly["revenue_musd"])

    plt.xlabel("Year")
    plt.ylabel("Average Revenue (Million USD)")
    plt.title("Yearly Box Office Performance")

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/yearly_box_office_trends.png")
    plt.close()



def plot_franchise_vs_standalone(df: pd.DataFrame):
    """
    Generates and saves a bar plot comparing franchise movies vs standalone movies.
    """
    plt.figure(figsize=(6, 5))

    plt.bar(
        df["franchise_type"],
        df["mean_revenue"]
    )

    plt.xlabel("Movie Type")
    plt.ylabel("Mean Revenue (Million USD)")
    plt.title("Franchise vs Standalone Revenue Comparison")

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/franchise_vs_standalone.png")
    plt.close()
