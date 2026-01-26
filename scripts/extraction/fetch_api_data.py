import requests
import pandas as pd
from configs import settings
from scripts.helpers import save_json
import time
import logging
from configs.logging_config import setup_logging

setup_logging()


movie_ids = [
    0, 299534, 19995, 140607, 299536, 597, 135397,
    420818, 24428, 168259, 99861, 284054, 12445,
    181808, 330457, 351286, 109445, 321612, 260513
]

def fetch_movie_data(movie_id, retries=3, timeout=10):
    """
        Fetch movie data from TMDB with retry and timeout handling.
    """
        
    url = f"{settings.BASE_URL}{movie_id}"

    parameters = {
        "api_key": settings.TMDB_API_KEY, 
        "append_to_response": "credits"
    }

    for attempt in range(1, retries +1):
        try:
            response = requests.get(url, params=parameters, timeout=timeout)
            response.raise_for_status() 
            logging.info(f"Fetched movie ID {movie_id}")
            return response.json()
                
        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt} failed for movie {movie_id}: {e}")
            time.sleep(2)
    logging.error(f"All {retries} attempts failed for movie {movie_id}.")
    return None


def run_extraction():
    all_data = []

    for movie_id in movie_ids:
        data = fetch_movie_data(movie_id)

        if data:
            all_data.append(data)
            save_json(data, f"{settings.RAW_DATA_DIR}/movie_{movie_id}.json")

    return pd.DataFrame(all_data)

if __name__ == "__main__":
    df = run_extraction()
