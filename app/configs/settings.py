from dotenv import load_dotenv
import os
from pathlib import Path
from typing import List


load_dotenv()

TMDB_API_KEY = os.getenv("API_KEY")
TMDB_BASE_URL = os.getenv(
    "TMDB_BASE_URL",
    "https://api.themoviedb.org/3/movie/",
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = Path(
    os.getenv(
        "TMDB_RAW_PATH",
        str(PROJECT_ROOT / "raw_data"),
    )
)


def _parse_movie_ids(raw_ids: str | None) -> List[int]:
    if not raw_ids:
        return []
    ids: List[int] = []
    for token in raw_ids.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            ids.append(int(token))
        except ValueError:
            continue
    return ids


TMDB_MOVIE_IDS = _parse_movie_ids(os.getenv("TMDB_MOVIE_IDS"))
