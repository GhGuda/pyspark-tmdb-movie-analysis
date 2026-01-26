from dotenv import load_dotenv
import os
from pathlib import Path




load_dotenv()


TMDB_API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.themoviedb.org/3/movie/"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "raw_data"