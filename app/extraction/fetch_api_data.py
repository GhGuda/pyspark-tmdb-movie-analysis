import time
from typing import Iterable

import requests

from configs import settings
from app.extraction.helpers import save_json
from app.utils.logging import get_logger


logger = get_logger("fetch-api-data")

DEFAULT_TIMEOUT = 10
DEFAULT_RETRIES = 3


def fetch_movie_data(
    movie_id: int,
    retries: int = DEFAULT_RETRIES,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict | None:
    """
    Fetch movie data from TMDB with retries.
    """
    url = f"{settings.TMDB_BASE_URL}{movie_id}"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "append_to_response": "credits"
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            logger.info(f"Fetched movie ID {movie_id}")
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.warning(
                f"Attempt {attempt}/{retries} failed for movie {movie_id}: {e}"
            )
            time.sleep(2)

    logger.error(f"All retries failed for movie {movie_id}")
    return None


def get_movie_ids() -> Iterable[int]:
    if settings.TMDB_MOVIE_IDS:
        return settings.TMDB_MOVIE_IDS
    logger.error(
        "No TMDB movie IDs configured. Set TMDB_MOVIE_IDS "
        "as a comma-separated list."
    )
    return []


def run_extraction() -> None:
    """
    Fetch TMDB movies and persist raw JSON files.
    """
    if not settings.TMDB_API_KEY:
        logger.error("TMDB API key missing. Set API_KEY in your environment.")
        return

    for movie_id in get_movie_ids():
        data = fetch_movie_data(movie_id)

        if data:
            save_json(
                data,
                f"{settings.RAW_DATA_DIR}/movie_{movie_id}.json"
            )


if __name__ == "__main__":
    run_extraction()
