# TMDB Movie Analysis (PySpark Pipeline)

## Overview

This project is a PySpark batch pipeline for extracting, enriching, and analyzing movie data from The Movie Database (TMDB). It follows a Bronze -> Silver -> Gold architecture, persists data as Parquet, and generates analytical visualizations using Pandas + Matplotlib.

## Architecture

`TMDB API -> Bronze (Raw JSON) -> Silver (Enriched Movies) -> Gold (KPIs & Aggregations) -> Visualizations (PNG)`

## Project Structure

```text
app/
  ingestion/            Spark JSON ingestion
  transformations/      Silver + Gold transformations
  analytics/            Rankings and aggregations
  spark_job/            Spark session factory
  utils/                Logging and data quality checks
  visualizations/       Plot generation
pipeline/
  tmdb_batch_pipeline.py
data/
  raw_data/             Bronze (raw TMDB JSON)
  processed/
    movies_enriched/    Silver Parquet
    analytics/          Gold Parquet
  plots/                Generated PNG plots
```

## Environment Variables

Create a `.env` file (copy from `.env.example`) with the following entries:

```env
TMDB_API_KEY=your_api_key_here
TMDB_BASE_URL=https://api.themoviedb.org/3/movie/
TMDB_MOVIE_IDS=299534,19995,140607
TMDB_MAX_WORKERS=5
TMDB_RATE_LIMIT_PER_SEC=4
TMDB_RAW_PATH=/opt/app/data/raw_data
TMDB_SILVER_PATH=/opt/app/data/processed/movies_enriched
TMDB_GOLD_PATH=/opt/app/data/processed/analytics
TMDB_PLOTS_PATH=data/plots
TMDB_DEBUG=false
```

## Quickstart (Spark Pipeline)

1. Build Docker image:

```bash
docker build -t tmdb-spark-batch -f DockerFile.spark-job .
```

2. Run Spark batch job:

```bash
docker run --rm -v ${PWD}/data:/opt/app/data tmdb-spark-batch
```

This will:

- Read raw TMDB JSON (Bronze)
- Produce enriched movies (Silver)
- Compute KPIs and analytics (Gold)
- Persist all outputs as Parquet

## Silver Layer (Enrichment)

The Silver dataset includes:

- Flattened nested TMDB fields
- Cleaned numeric columns
- Monetary values converted to million USD
- Extracted genres, collections, cast, and crew
- Derived dimensions such as `franchise_type`

## Gold Layer (Analytics & KPIs)

### KPIs

- Profit = Revenue - Budget
- ROI = Profit / Budget
- Budget and revenue normalized to million USD

### Aggregations

- Franchise vs standalone performance
- Most successful franchises
- Most successful directors
- Top movies by ROI

## Outputs

```text
data/processed/analytics/
  movies_with_kpis/
  top_movies_by_roi/
  franchise_vs_standalone/
  most_successful_franchises/
  most_successful_directors/
```

## Visualizations

Visualizations are generated after the Spark job using Parquet outputs.

### Run Visualizations

```bash
py -m app.visualizations.run_visualizations
```

### Generated Plots

- `revenue_vs_budget.png`
- `roi_distribution_by_genre.png`
- `popularity_vs_rating.png`
- `yearly_box_office_trends.png`
- `franchise_vs_standalone.png`

## Data Quality Checks

The pipeline enforces:

- Non-empty datasets
- Mandatory keys (`id`, `title`) in Silver
- Safe handling of nulls in KPIs

## Notes

- Spark writes Parquet as directories, not single files.
- Container paths (`/opt/app/...`) can be overridden locally via environment variables.

## Testing

Install dev dependencies:

```bash
pip install -r requirements.dev.txt
```

Run tests:

```bash
pytest -q
```
