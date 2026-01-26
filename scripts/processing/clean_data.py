import pandas as pd
import numpy as np
from pathlib import Path
import json
import logging



def load_movies_from_raw_data(raw_data_dir="../raw_data"):
    """
    Load raw TMDB movie JSON files from disk into a pandas DataFrame.

    This function is responsible ONLY for reading raw JSON files
    that were previously extracted from the TMDB API and saved to disk.
    No cleaning or transformation is performed here.

    Args:
        raw_data_dir (str): Relative path to the raw_data directory.

    Returns:
        pd.DataFrame: DataFrame containing raw movie records.
                      Returns an empty DataFrame if loading fails.
    """
    try:
        raw_path = Path(raw_data_dir)
        json_files = raw_path.glob("*.json")

        movies = []
        for file in json_files:
            with open(file, "r", encoding="utf-8") as f:
                movies.append(json.load(f))

        df = pd.DataFrame(movies)

        if df.empty:
            logging.warning("No movie data found in raw_data folder")

        return df

    except Exception as e:
        logging.error(f"Failed to load raw movie data: {e}")
        return pd.DataFrame()



def drop_irrelevant_columns(movies_df):
    """
    Remove columns that are not required for analysis.

    This reduces noise in the dataset and improves clarity for
    downstream analysis.

    Args:
        movies_df (pd.DataFrame): Raw movie DataFrame.

    Returns:
        pd.DataFrame: DataFrame with irrelevant columns removed.
    """
    try:
        drop_columns = [
            'adult',
            'imdb_id',
            'original_title',
            'video',
            'homepage'
        ]

        return movies_df.drop(columns=drop_columns, errors='ignore')

    except Exception as e:
        logging.error(f"Error dropping irrelevant columns: {e}")
        return movies_df



def extract_name(value, key="name"):
    """
    Extract readable name values from nested TMDB fields.

    TMDB returns many attributes as lists or dictionaries.
    This helper converts them into pipe-separated strings.

    Args:
        value (list | dict | str): Raw value from TMDB response.
        key (str): Dictionary key to extract.

    Returns:
        str | NaN: Extracted string or NaN if extraction fails.
    """
    try:
        # Already processed (string)
        if isinstance(value, str):
            return value

        # List of dictionaries
        if isinstance(value, list):
            values = [item.get(key, "") for item in value if isinstance(item, dict)]
            return "|".join(values)

        # Single dictionary
        if isinstance(value, dict):
            return value.get(key, "")

        return np.nan

    except Exception as e:
        logging.error(f"Error extracting names: {e}")
        return np.nan



def extracting_name_from_columns(movies_df):
    """
    Normalize nested TMDB columns by extracting readable names.

    This function standardizes multiple TMDB fields that contain
    nested lists or dictionaries.

    Args:
        movies_df (pd.DataFrame): Movie DataFrame.

    Returns:
        pd.DataFrame: DataFrame with normalized string columns.
    """
    try:
        columns = [
            'belongs_to_collection',
            'genres',
            'production_countries',
            'production_companies',
            'spoken_languages'
        ]

        for column in columns:
            if column in movies_df.columns:
                movies_df[column] = movies_df[column].apply(
                    lambda value: extract_name(value)
                )

        return movies_df
    
    except Exception as e:
        logging.error(f"Error extracting names from columns: {e}")
        return movies_df



def check_anomalies(movies_df):
    """
        Inspect high-level value distributions for selected categorical columns.

        This function is intended for exploratory diagnostics and
        sanity checks during analysis.

        Args:
            movies_df (pd.DataFrame): Movie DataFrame.

        Returns:
            dict: Dictionary of value counts per column.
    """
    try:
        columns = [
            'genres',
            'spoken_languages',
            'production_companies',
            'production_countries',
            'belongs_to_collection'
        ]
        
        result = {}
        for col in columns:
            # value_counts shows the top values including NaN
            result[col] = [movies_df[col].value_counts()]
        return result
    except Exception as e:
        logging.error(f"Error checking anomalies: {e}")
        return {}
       


def convert_column_datatypes(movies_df):
    """
    Convert numeric and datetime columns to appropriate data types.

    This ensures correct mathematical operations and time-based analysis.

    Args:
        movies_df (pd.DataFrame): Movie DataFrame.

    Returns:
        pd.DataFrame: DataFrame with corrected data types.
    """
    try:
        numeric_cols = [
            'budget',
            'revenue',
            'popularity',
            'id',
            'vote_count',
            'vote_average',
            'runtime'
        ]

        for col in numeric_cols:
            if col in movies_df.columns:
                movies_df[col] = pd.to_numeric(movies_df[col], errors='coerce')

        movies_df['release_date'] = pd.to_datetime(
            movies_df['release_date'], errors='coerce'
        )

        return movies_df

    except Exception as e:
        logging.error(f"Error converting column data types: {e}")
        return movies_df



def replacing_unrealistic_values(movies_df):
    """
    Handle unrealistic or placeholder values and create derived metrics.

    Operations performed:
    - Replace zero budgets, revenue, runtime with NaN
    - Convert budget and revenue to millions
    - Handle zero vote counts
    - Clean placeholder text fields

    Args:
        movies_df (pd.DataFrame): Movie DataFrame.

    Returns:
        pd.DataFrame: Cleaned DataFrame with derived metrics.
    """
    try:
        for col in ['budget', 'revenue', 'runtime']:
            if col in movies_df.columns:
                movies_df[col] = movies_df[col].replace(0, np.nan)

        movies_df['budget_musd'] = movies_df['budget'] / 1_000_000
        movies_df['revenue_musd'] = movies_df['revenue'] / 1_000_000

        movies_df.loc[movies_df['vote_count'] == 0, 'vote_average'] = np.nan

        placeholders = ["No Data", "", "N/A", "na", "null"]
        for col in ['overview', 'tagline']:
            if col in movies_df.columns:
                movies_df[col] = movies_df[col].replace(placeholders, np.nan)

        return movies_df

    except Exception as e:
        logging.error(f"Error replacing unrealistic values: {e}")
        return movies_df



def clean_movies(movies_df):
    """
    Perform final dataset cleaning and filtering.

    Cleaning rules:
    - Remove duplicates
    - Remove rows with missing ID or title
    - Keep movies with sufficient data completeness
    - Keep only released movies

    Args:
        movies_df (pd.DataFrame): Movie DataFrame.

    Returns:
        pd.DataFrame: Final cleaned dataset.
    """
    try:
        movies_df = (
            movies_df
            .drop_duplicates(subset=['id', 'title'])
            .dropna(subset=['id', 'title'])
            .dropna(thresh=10)
        )

        if 'status' in movies_df.columns:
            movies_df = movies_df[movies_df['status'] == 'Released'].drop(columns=['status'])

        return movies_df

    except Exception as e:
        logging.error(f"Error cleaning movie dataset: {e}")
        return movies_df



def extract_cast_and_crew(movies_df):
    """
        Extract cast and crew metadata from the TMDB credits field.

        Adds:
        - cast names
        - cast size
        - director name(s)
        - crew size

        Args:
            movies_df (pd.DataFrame): Movie DataFrame.

        Returns:
            pd.DataFrame: DataFrame enriched with cast and crew features.
    """
    try:
        movies_df["cast"] = movies_df["credits"].apply(
            lambda x: "|".join([c["name"] for c in x.get("cast", [])]) if isinstance(x, dict) else None
        )

        movies_df["cast_size"] = movies_df["credits"].apply(
            lambda x: len(x.get("cast", [])) if isinstance(x, dict) else 0
        )

        movies_df["director"] = movies_df["credits"].apply(
            lambda x: "|".join([c["name"] for c in x.get("crew", []) if c.get("job") == "Director"])
            if isinstance(x, dict) else None
        )

        movies_df["crew_size"] = movies_df["credits"].apply(
            lambda x: len(x.get("crew", [])) if isinstance(x, dict) else 0
        )

        return movies_df
    except Exception as e:
        logging.error(f"Error extracting cast and crew data: {e}")
        return movies_df



def reorder_columns(movies_df):
    """
        Reorder columns to improve readability and presentation.

        Args:
            movies_df (pd.DataFrame): Movie DataFrame.

        Returns:
            pd.DataFrame: DataFrame with reordered columns.
    """
    try:
        ordered_columns = [
            'id', 'title', 'tagline', 'release_date', 'genres',
            'belongs_to_collection', 'original_language',
            'budget_musd', 'revenue_musd',
            'production_companies', 'production_countries',
            'vote_count', 'vote_average', 'popularity',
            'runtime', 'overview', 'spoken_languages',
            'poster_path', 'cast', 'cast_size',
            'director', 'crew_size'
        ]


        cols_present = [col for col in ordered_columns if col in movies_df.columns]

        return movies_df.reindex(columns=cols_present)
    
    except Exception as e:
        logging.error(f"Error reordering columns: {e}")
        return movies_df

