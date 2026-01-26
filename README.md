# TMDB Movie Analysis

This project is a comprehensive ETL (Extract, Transform, Load) and analysis tool that fetches movie details from The Movie Database (TMDB), stores raw JSON data, and provides various KPI (Key Performance Indicator) helpers along with an analysis notebook for deeper insights.

## Contents
- [Project Structure](#project-structure)
- [Quickstart](#quickstart)
- [Usage](#usage)
- [Key Files & Helpers](#key-files--helpers)
- [Notes](#notes)

## Project Structure
- [configs/settings.py](configs/settings.py) — Configuration file with environment variables.
- [scripts/extraction/fetch_api_data.py](scripts/extraction/fetch_api_data.py) — Script for extracting movie data from TMDB.
- [scripts/helpers.py](scripts/helpers.py) — Utility functions for saving and loading JSON data.
- [scripts/kpi.py](scripts/kpi.py) — Functions for calculating KPIs related to movie performance.
- [notebooks/analysis.ipynb](notebooks/analysis.ipynb) — Main analysis notebook for data exploration and visualization.
- [raw_data/](raw_data/) — Directory containing raw JSON responses from TMDB (e.g., [raw_data/movie_299534.json](raw_data/movie_299534.json)).
- [requirements.txt](requirements.txt) — List of dependencies required for the project.
- .env — Local environment file for storing sensitive information like API keys.

## Quickstart
1. Create or activate a virtual environment (or use the provided `env/`).
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Add your TMDB API key to the `.env` file as `API_KEY` or set it as an environment variable.
4. Run the extraction script:
   ```sh
   python scripts/extraction/fetch_api_data.py
   ```
   This will fetch movie data and save the JSON files to the `raw_data/` directory.

## Usage
- Open the [notebooks/analysis.ipynb](notebooks/analysis.ipynb) to reproduce the data cleaning, merging, and KPI calculations.
- Utilize the KPI helpers in [scripts/kpi.py](scripts/kpi.py) to rank movies and compute profit/ROI.

### Example Usage
- Load raw JSON data into a DataFrame (demonstrated in the notebook).
- Call `add_profit_columns` to compute profit and ROI.
- Use `rank_movies` to retrieve the top-N movies based on a specified metric.

## Key Files & Helpers
- **configs/settings.py** exposes:
  - `TMDB_API_KEY`
  - `BASE_URL`
  - `RAW_DATA_DIR`
  
- **scripts/extraction/fetch_api_data.py** contains:
  - `fetch_movie_data`
  - `run_extraction`
  
- **scripts/helpers.py** contains:
  - `save_json`
  - `load_json`
  
- **scripts/kpi.py** contains:
  - `rank_movies`
  - `add_profit_columns`

## Notes
- Raw JSON files are stored in the `raw_data/` directory. Examples include [raw_data/movie_299534.json](raw_data/movie_299534.json) and [raw_data/movie_140607.json](raw_data/movie_140607.json).
- The helpers ensure that JSON data is written in a readable format. Refer to `save_json` for details.
- Configuration settings are read from the `.env` file using `python-dotenv`. See `requirements.txt` for more information.

## References
- Configuration settings: [`TMDB_API_KEY`, `BASE_URL`, `RAW_DATA_DIR`](configs/settings.py)
- Data extraction functions: [`fetch_movie_data`, `run_extraction`](scripts/extraction/fetch_api_data.py)
- JSON helpers: [`save_json`, `load_json`](scripts/helpers.py)
- KPI functions: [`rank_movies`, `add_profit_columns`](scripts/kpi.py)

## Quickstart
1. Create / activate a virtual environment (or use the provided `env/`).
2. Install dependencies:
```sh
pip install -r 

3. Add your TMDB API key to .env as API_KEY (or set env var).
4. Run extraction:
python

This will call the functions in scripts/fetch_api_data.py and save JSON to the raw_data/ folder.

Usage
Open notebooks/01_api_extraction.ipynb to reproduce cleaning, merging and KPI calculations.
Use KPI helpers in scripts/kpi.py to rank movies and compute profit/ROI.
Example:

Load raw JSON into a DataFrame (notebook shows this).
Call add_profit_columns to compute profit and roi.
Call rank_movies to get top-N by a metric.
Key files & helpers
configs/settings.py exposes:
TMDB_API_KEY
BASE_URL
RAW_DATA_DIR
scripts/fetch_api_data.py contains:
fetch_movie_data
run_extraction
scripts/helpers.py contains:
save_json
load_json
scripts/kpi.py contains:
rank_movies
add_profit_columns
Exploratory analysis available in notebooks/01_api_extraction.ipynb.
Notes
Raw JSON files are in raw_data/. Examples: raw_data/movie_299534.json, raw_data/movie_140607.json.
Helpers write readable JSON. See save_json.
Config reads .env via python-dotenv. See requirements.txt.

References (open files / symbols)
-  — [`TMDB_API_KEYBASE_URLRAW_DATA_DIR`](configs/settings.py)  
-  — [`fetch_movie_datarun_extraction`](scripts/fetch_api_data.py)  
-  — [`save_jsonload_json`](scripts/helpers.py)  
-  — [`rank_moviesadd_profit_columns`](scripts/kpi.py)  
-   
-   
-   
- , , 