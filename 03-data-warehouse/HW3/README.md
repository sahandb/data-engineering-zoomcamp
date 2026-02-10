# HW3: Data Warehousing & BigQuery

Full instructions: [homework.md](./homework.md)

## What’s here

| File | Purpose |
|------|--------|
| **HW3.ipynb** | Homework answers and BigQuery queries (Python + BQ client). |
| **homework.md** | Official homework text and questions. |
| **load_yellow_taxi_data.py** | Download Jan–Jun 2024 yellow taxi parquet and upload to GCS. |
| **download_yellow_taxi_data.py** | Download parquet files only (no GCS). Output in `data/`. |
| **DLT_upload_to_GCP.ipynb** | DLT-based load to GCS/BigQuery (from cohort; Colab-oriented). |
| **data/** | Local parquet files (6 files, Jan–Jun 2024) after running `download_yellow_taxi_data.py`. |

## Setup

```bash
conda activate dataTalks
pip install -r requirements.txt
```

## 1. Get the data

- **Local only:**  
  `python download_yellow_taxi_data.py`  
  Puts 6 parquet files in `data/`.

- **Into GCS (for BigQuery):**  
  Set `GCS_BUCKET` (or edit `BUCKET_NAME` in the script). Use a service account JSON or `gcloud auth application-default login`, then run:  
  `python load_yellow_taxi_data.py`  
  (Downloads and uploads to your bucket.)

## 2. Run the homework

1. In **HW3.ipynb**, set `PROJECT`, `DATASET`, `BUCKET` in the first code cell.
2. Ensure GCP auth: `gcloud auth application-default login` (or set `GOOGLE_APPLICATION_CREDENTIALS`).
3. Run the notebook (create external table from GCS, then materialized table, then answer questions).

## Data source

Yellow Taxi Trip Records Jan–Jun 2024:  
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page  
Parquet base URL: `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-{01..06}.parquet`
