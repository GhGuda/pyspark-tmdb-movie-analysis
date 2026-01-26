import requests
import time
from configs import settings
from app.extraction.helpers import save_json

from app.utils.logging import get_logger


logger = get_logger("fetch-api-data")

movie_ids = [
    0, 299534, 19995, 140607, 299536, 597, 135397,
    420818, 24428, 168259, 99861, 284054, 12445,
    181808, 330457, 351286, 109445, 321612, 260513
]


def fetch_movie_data(movie_id: int, retries: int = 3, timeout: int = 10) -> dict | None:
    """
    Fetch movie data from TMDB with retries.
    """
    url = f"{settings.BASE_URL}{movie_id}"
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


def run_extraction() -> None:
    """
    Fetch TMDB movies and persist raw JSON files.
    """
    for movie_id in movie_ids:
        data = fetch_movie_data(movie_id)

        if data:
            save_json(
                data,
                f"{settings.RAW_DATA_DIR}/movie_{movie_id}.json"
            )


if __name__ == "__main__":
    run_extraction()
