import os
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable

import requests

from app.configs import settings
from app.extraction.helpers import save_json
from app.utils.logging import get_logger


logger = get_logger("fetch-api-data")

DEFAULT_TIMEOUT = 10
DEFAULT_RETRIES = 3
DEFAULT_MAX_WORKERS = 5
DEFAULT_RATE_LIMIT_PER_SEC = 4


def fetch_movie_data(
    movie_id: int,
    retries: int = DEFAULT_RETRIES,
    timeout: int = DEFAULT_TIMEOUT,
    backoff_base: float = 1.0,
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
            sleep_for = backoff_base * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
            time.sleep(sleep_for)

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

    movie_ids = list(get_movie_ids())
    if not movie_ids:
        return

    max_workers = int(
        os.getenv("TMDB_MAX_WORKERS", str(DEFAULT_MAX_WORKERS))
    )
    rate_limit = float(
        os.getenv("TMDB_RATE_LIMIT_PER_SEC", str(DEFAULT_RATE_LIMIT_PER_SEC))
    )
    delay_between_requests = 1.0 / rate_limit if rate_limit > 0 else 0.0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for movie_id in movie_ids:
            futures[executor.submit(fetch_movie_data, movie_id)] = movie_id
            if delay_between_requests:
                time.sleep(delay_between_requests)

        for future in as_completed(futures):
            movie_id = futures[future]
            try:
                data = future.result()
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed for movie {movie_id}: {e}")
                continue
            except Exception as e:
                logger.exception(f"Unexpected error for movie {movie_id}: {e}")
                continue

            if data:
                save_json(
                    data,
                    f"{settings.RAW_DATA_DIR}/movie_{movie_id}.json"
                )


if __name__ == "__main__":
    run_extraction()
