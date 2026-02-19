TMDB Movie Analysis (PySpark Pipeline)

This project is a production-ready PySpark batch pipeline for extracting, enriching, and analyzing movie data from The Movie Database (TMDB).
It follows a Bronze → Silver → Gold architecture, persists data as Parquet, and generates analytical visualizations using Pandas + Matplotlib.

📌 Architecture Overview
TMDB API
   ↓
Bronze (Raw JSON)
   ↓
Silver (Enriched Movies)
   ↓
Gold (KPIs & Aggregations)
   ↓
Visualizations (PNG)


Bronze: Raw TMDB JSON responses

Silver: Cleaned, flattened, analysis-ready movie data

Gold: KPIs, rankings, and aggregations

Visualizations: Offline plots generated from Parquet outputs

📂 Project Structure
```bash
.
├── app/
│   ├── ingestion/
│   │   └── tmdb_loader.py          # Spark JSON ingestion
│   ├── transformations/
│   │   ├── enrichments.py          # Silver transformations
│   │   └── kpis.py                 # KPI calculations (Gold)
│   ├── analytics/
│   │   └── rankings.py             # Rankings & aggregations
│   ├── spark_job/
│   │   └── session.py              # Spark session factory
│   ├── utils/
│   │   ├── logging.py              # Structured logging
│   │   └── data_quality.py         # Data quality checks
│   ├── visualizations/
│   │   ├── generate_plots.py       # Matplotlib plots
│   │   └── run_visualizations.py   # Visualization runner
│
├── pipeline/
│   └── tmdb_batch_pipeline.py      # Main Spark batch pipeline
│
├── data/
│   ├── raw_data/                   # Bronze (raw TMDB JSON)
│   ├── processed/
│   │   ├── movies_enriched/        # Silver Parquet
│   │   └── analytics/              # Gold Parquet
│   └── plots/                      # Generated PNG plots
│
├── DockerFile.spark-job             # Spark batch Docker image
├── requirements.spark.txt           # Spark dependencies
├── requirements.viz.txt             # Visualization dependencies
├── .env                             # Environment variables
└── README.md
```
⚙️ Technologies Used

PySpark 3.5

Apache Spark (Dockerized)

Parquet

Pandas & Matplotlib (visualizations only)

TMDB REST API

Docker

🔑 Environment Variables

Create a .env file:

TMDB_API_KEY=your_api_key_here
TMDB_RAW_PATH=/opt/app/data/raw_data
TMDB_SILVER_PATH=/opt/app/data/processed/movies_enriched
TMDB_GOLD_PATH=/opt/app/data/processed/analytics
TMDB_PLOTS_PATH=data/plots

🚀 Quickstart (Spark Pipeline)
1️⃣ Build Docker Image
docker build -t tmdb-spark-batch -f DockerFile.spark-job .

2️⃣ Run Spark Batch Job
docker run --rm \
  -v ${PWD}/data:/opt/app/data \
  tmdb-spark-batch


This will:

Read raw TMDB JSON (Bronze)

Produce enriched movies (Silver)

Compute KPIs & analytics (Gold)

Persist all outputs as Parquet

🧪 Silver Layer (Enrichment)

The Silver dataset includes:

Flattened nested TMDB fields

Cleaned numeric columns

Converted monetary values to million USD

Extracted genres, collections, cast, crew

Derived dimensions such as franchise_type

Output:

data/processed/movies_enriched/

📊 Gold Layer (Analytics & KPIs)
KPIs

Profit = Revenue − Budget

ROI = Profit / Budget

Budget & revenue normalized to million USD

Aggregations

Franchise vs Standalone performance

Most successful franchises

Most successful directors

Top movies by ROI

Outputs:
```bash
data/processed/analytics/
├── movies_with_kpis
├── top_movies_by_roi
├── franchise_vs_standalone
├── most_successful_franchises
└── most_successful_directors
```
📈 Visualizations (Step 4)

Visualizations are generated after the Spark job, using Parquet outputs.

Run Visualizations
py -m app.visualizations.run_visualizations

Generated Plots

Revenue vs Budget

ROI Distribution by Genre

Popularity vs Rating

Yearly Box Office Trends

Franchise vs Standalone Comparison

Output:
```bash
data/plots/
├── revenue_vs_budget.png
├── roi_distribution_by_genre.png
├── popularity_vs_rating.png
├── yearly_box_office_trends.png
└── franchise_vs_standalone.png
```
🧹 Data Quality Checks

The pipeline enforces:

Non-empty datasets

Mandatory keys (id, title) in Silver

Safe handling of nulls in KPIs

Schema consistency across layers

Failures stop the pipeline early with structured logs.

🧠 Design Principles

Spark for computation

Parquet for storage

Pandas only for plotting

No transformations inside notebooks

Clear separation of Bronze / Silver / Gold

Function-based Spark transformations (.transform)

📌 Notes

Spark writes Parquet as directories, not single files.

Visualization scripts auto-detect available datasets.

Container paths (/opt/app/...) are overridden locally via env vars.

This project is suitable for production pipelines and portfolios.

✅ Status

✔ End-to-end pipeline
✔ Dockerized Spark job
✔ Clean data contracts
✔ Reproducible analytics
✔ Visual reporting
