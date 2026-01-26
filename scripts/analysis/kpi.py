import pandas as pd
import logging
import numpy as np


def rank_movies(df, by, top=True, n=10, condition=None, new_col_name=None):
    """
    Rank movies based on a column.
    
    Parameters:
        df (DataFrame): Movies dataframe
        by (str or list): Column(s) to sort by
        top (bool): True → highest values, False → lowest
        n (int): Number of rows to return
        condition (callable, optional): Function to filter df before ranking
        new_col_name (str, optional): Add a column to label KPI
    
    Returns:
        DataFrame: Top/bottom ranked movies
    """
    try:
        data = df.copy()
        df_filtered = data if condition is None else data[condition(data)]
        ranked = df_filtered.sort_values(by=by, ascending=not top).head(n)
        if new_col_name:
            ranked["KPI"] = new_col_name
        return ranked
    except Exception as e:
        logging.error(f"rank_movies failed: {e}")
        return pd.DataFrame()



def best_rated_sci_fi_movies(df):
    """
    Retrieve best-rated Sci-Fi Action movies starring Bruce Willis.

    Args:
        df (pd.DataFrame): Analysis-ready movie dataset.

    Returns:
        pd.DataFrame: Filtered and sorted movies.
    """

    try:
        filtered_df = df[
            df['genres'].str.contains("Science Fiction", case=False, na=False) &
            df['genres'].str.contains("Action", case=False, na=False) &
            df['cast'].str.contains("Bruce Willis", case=False, na=False)
        ].sort_values(by='vote_average', ascending=False)

        return filtered_df

    except Exception as e:
        logging.error(f"best_rated_sci_fi_movies failed: {e}")
        return pd.DataFrame()



def uma_thurman_tarantino_movies(df):
    """
    Retrieve movies starring Uma Thurman directed by Quentin Tarantino.

    Args:
        df (pd.DataFrame): Analysis-ready movie dataset.

    Returns:
        pd.DataFrame: Filtered movies sorted by runtime.
    """

    try:
        filtered_df = df[
            df['cast'].str.contains("Uma Thurman", case=False, na=False) &
            df['director'].str.contains("Quentin Tarantino", case=False, na=False)
        ].sort_values(by='runtime', ascending=True)

        return filtered_df

    except Exception as e:
        logging.error(f"uma_thurman_tarantino_movies failed: {e}")
        return pd.DataFrame()



def compare_franchise_vs_standalone_performance(df):
    """
    Compare franchise vs standalone movie performance.

    Args:
        df (pd.DataFrame): Analysis-ready movie dataset.

    Returns:
        pd.DataFrame: Aggregated comparison metrics.
    """
    try:
        data = df.copy()

        data['franchise_type'] = data['belongs_to_collection'].apply(
            lambda x: 'Franchise' if pd.notna(x) else 'Standalone'
        )
        # Calculate ROI safely
        data["roi"] = (data["revenue_musd"] - data["budget_musd"]) / data["budget_musd"].replace([np.inf, -np.inf], np.nan)

        comparison = data.groupby('franchise_type').agg(
            mean_revenue=('revenue_musd', 'mean'),
            median_roi=('roi', 'median'),
            mean_budget=('budget_musd', 'mean'),
            mean_popularity=('popularity', 'mean'),
            mean_rating=('vote_average', 'mean')
        ).sort_values(by='mean_revenue', ascending=False)

        return comparison

    except Exception as e:
        logging.error(f"compare_franchise_vs_standalone failed: {e}")
        return pd.DataFrame()
    
    

def most_successful_franchises(df):
    """
    Compute performance metrics for movie franchises.

    Args:
        df (pd.DataFrame): Analysis-ready movie dataset.

    Returns:
        pd.DataFrame: Franchise-level aggregated statistics.
    """
    try:
        data = df.copy()
        data['collection_name'] = data['belongs_to_collection']
        franchise_df = data[data['collection_name'].notna()]

        franchise_stats = franchise_df.groupby('collection_name').agg(
            total_movies=('id', 'count'),
            total_budget=('budget_musd', 'sum'),
            mean_budget=('budget_musd', 'mean'),
            total_revenue=('revenue_musd', 'sum'),
            mean_revenue=('revenue_musd', 'mean'),
            mean_rating=('vote_average', 'mean')
        ).sort_values(by='mean_revenue', ascending=False)

        return franchise_stats

    except Exception as e:
        logging.error(f"most_successful_franchises failed: {e}")
        return pd.DataFrame()



def most_successful_directors(df):
    """
    Compute performance metrics for movie directors.

    Args:
        df (pd.DataFrame): Analysis-ready movie dataset.

    Returns:
        pd.DataFrame: Director-level aggregated statistics.
    """
    try:
        data = df.copy()
        data = data[data['director'].notna()]

        director_stats = data.groupby('director').agg(
            total_movies=('id', 'count'),
            total_revenue=('revenue_musd', 'sum'),
            mean_rating=('vote_average', 'mean')
        ).sort_values(by='total_revenue', ascending=False)

        return director_stats

    except Exception as e:
        logging.error(f"most_successful_directors failed: {e}")
        return pd.DataFrame()



def get_all_kpis(df, n=10):
    """
    Compute all KPIs required for Step 3: KPI Implementation & Analysis.

    Args:
        df (pd.DataFrame): Analysis-ready movie dataset
        n (int): Number of records per KPI

    Returns:
        dict: Dictionary of KPI DataFrames
    """
    try:
        kpis = {}

        # Work on a copy for derived metrics
        df_kpi = df.copy()

        # --------------------------------------------------
        # Derived metrics
        # --------------------------------------------------
        df_kpi["profit"] = df_kpi["revenue_musd"] - df_kpi["budget_musd"]
        df_kpi["roi"] = ((df_kpi["revenue_musd"] - df_kpi["budget_musd"]) / df_kpi["budget_musd"]).replace([np.inf, -np.inf], np.nan)

        # --------------------------------------------------
        # KPI conditions
        # --------------------------------------------------
        roi_condition = lambda x: x["budget_musd"] >= 10
        rating_condition = lambda x: x["vote_count"] >= 10

        # --------------------------------------------------
        # KPI calculations
        # --------------------------------------------------
        kpis["highest_revenue"] = rank_movies(
            df_kpi, by="revenue_musd", top=True, n=n,
            new_col_name="Highest Revenue"
        )

        kpis["highest_budget"] = rank_movies(
            df_kpi, by="budget_musd", top=True, n=n,
            new_col_name="Highest Budget"
        )

        kpis["highest_profit"] = rank_movies(
            df_kpi, by="profit", top=True, n=n,
            new_col_name="Highest Profit"
        )

        kpis["lowest_profit"] = rank_movies(
            df_kpi, by="profit", top=False, n=n,
            new_col_name="Lowest Profit"
        )

        kpis["highest_roi"] = rank_movies(
            df_kpi, by="roi", top=True, n=n,
            condition=roi_condition,
            new_col_name="Highest ROI (Budget ≥ 10M)"
        )

        kpis["lowest_roi"] = rank_movies(
            df_kpi, by="roi", top=False, n=n,
            condition=roi_condition,
            new_col_name="Lowest ROI (Budget ≥ 10M)"
        )

        kpis["most_voted"] = rank_movies(
            df_kpi, by="vote_count", top=True, n=n,
            new_col_name="Most Voted Movies"
        )

        kpis["highest_rated"] = rank_movies(
            df_kpi, by="vote_average", top=True, n=n,
            condition=rating_condition,
            new_col_name="Highest Rated (≥10 votes)"
        )

        kpis["lowest_rated"] = rank_movies(
            df_kpi, by="vote_average", top=False, n=n,
            condition=rating_condition,
            new_col_name="Lowest Rated (≥10 votes)"
        )

        kpis["most_popular"] = rank_movies(
            df_kpi, by="popularity", top=True, n=n,
            new_col_name="Most Popular Movies"
        )

        return kpis

    except Exception as e:
        logging.error(f"get_all_kpis failed: {e}")
        return {}
