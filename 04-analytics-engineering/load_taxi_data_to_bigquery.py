#!/usr/bin/env python3
"""
Load green and yellow NYC taxi data (2019-2020) from DataTalksClub into BigQuery.

Use this for Module 4 (Analytics Engineering) when using the Cloud setup (BigQuery).
Downloads CSV.gz from DataTalksClub, converts to Parquet, uploads to GCS, loads into
BigQuery dataset nytaxi as green_tripdata and yellow_tripdata (so dbt can use them).

Usage:
  Set GCP_PROJECT_ID, GCS_BUCKET (and optionally BQ_DATASET, BQ_LOCATION), then:
  pip install google-cloud-bigquery google-cloud-storage requests duckdb
  python load_taxi_data_to_bigquery.py
"""

import os
import sys
from pathlib import Path

# --- Config (override with env vars) ---
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "project-3a3cf597-6dcd-4db6-8c0")
GCS_BUCKET = os.environ.get("GCS_BUCKET", "dezoomcamp-hw3-3a3cf597")
BQ_DATASET = os.environ.get("BQ_DATASET", "nytaxi")
BQ_LOCATION = os.environ.get("BQ_LOCATION", "US")  # Match your dataset location (e.g. US, EU, us-central1)
DATA_DIR = Path(os.environ.get("DATA_DIR", "data_taxi_2019_2020"))

BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download"
TAXI_TYPES = ["yellow", "green"]
YEARS = [2019, 2020]
MONTHS = list(range(1, 13))


def download_and_convert(taxi_type: str) -> list[Path]:
    """Download CSV.gz from DataTalksClub, convert to Parquet. Returns list of parquet paths."""
    import requests
    import duckdb

    data_dir = DATA_DIR / taxi_type
    data_dir.mkdir(parents=True, exist_ok=True)
    parquet_paths = []

    for year in YEARS:
        for month in MONTHS:
            csv_gz_name = f"{taxi_type}_tripdata_{year}-{month:02d}.csv.gz"
            parquet_name = f"{taxi_type}_tripdata_{year}-{month:02d}.parquet"
            parquet_path = data_dir / parquet_name
            csv_gz_path = data_dir / csv_gz_name

            if parquet_path.exists():
                print(f"  Skip (exists): {parquet_name}")
                parquet_paths.append(parquet_path)
                continue

            url = f"{BASE_URL}/{taxi_type}/{csv_gz_name}"
            try:
                print(f"  Downloading {csv_gz_name}...")
                resp = requests.get(url, stream=True, timeout=120)
                resp.raise_for_status()
                with open(csv_gz_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)
            except Exception as e:
                print(f"  Failed to download {url}: {e}")
                continue

            try:
                print(f"  Converting to {parquet_name}...")
                con = duckdb.connect()
                csv_path = csv_gz_path.as_posix()
                pq_path = parquet_path.as_posix()
                # Cast numeric columns that CSV may give as string so BigQuery accepts them
                try:
                    con.execute(f"""
                        COPY (
                            SELECT * REPLACE(
                                TRY_CAST(congestion_surcharge AS DOUBLE) AS congestion_surcharge,
                                TRY_CAST(improvement_surcharge AS DOUBLE) AS improvement_surcharge,
                                TRY_CAST(ehail_fee AS DOUBLE) AS ehail_fee
                            )
                            FROM read_csv_auto('{csv_path}')
                        )
                        TO '{pq_path}' (FORMAT PARQUET)
                    """)
                except Exception:
                    con.execute(f"""
                        COPY (SELECT * FROM read_csv_auto('{csv_path}'))
                        TO '{pq_path}' (FORMAT PARQUET)
                    """)
                con.close()
            except Exception as e:
                print(f"  Failed to convert: {e}")
                continue

            csv_gz_path.unlink(missing_ok=True)
            parquet_paths.append(parquet_path)
            print(f"  Done: {parquet_name}")

    return parquet_paths


def upload_to_gcs(parquet_paths: list[Path], gcs_prefix: str) -> list[str]:
    """Upload parquet files to GCS. Returns list of gs:// URIs."""
    from google.cloud import storage

    creds_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_file and os.path.isfile(creds_file):
        client = storage.Client.from_service_account_json(creds_file, project=GCP_PROJECT_ID)
    else:
        client = storage.Client(project=GCP_PROJECT_ID)

    bucket = client.bucket(GCS_BUCKET)
    uris = []
    for p in parquet_paths:
        blob_name = f"{gcs_prefix}/{p.name}"
        blob = bucket.blob(blob_name)
        print(f"  Uploading {p.name} -> gs://{GCS_BUCKET}/{blob_name}")
        blob.upload_from_filename(str(p), content_type="application/octet-stream")
        uris.append(f"gs://{GCS_BUCKET}/{blob_name}")
    return uris


def load_bigquery_table(taxi_type: str, source_uris: list[str]) -> None:
    """Load Parquet files from GCS into BigQuery table nytaxi.{green,yellow}_tripdata."""
    from google.cloud import bigquery

    creds_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_file and os.path.isfile(creds_file):
        client = bigquery.Client.from_service_account_json(creds_file, project=GCP_PROJECT_ID)
    else:
        client = bigquery.Client(project=GCP_PROJECT_ID)

    table_id = f"{GCP_PROJECT_ID}.{BQ_DATASET}.{taxi_type}_tripdata"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    print(f"  Loading {len(source_uris)} file(s) into {table_id}...")
    # location must match your dataset (e.g. US, EU, us-central1)
    load_job = client.load_table_from_uri(
        source_uris, table_id, job_config=job_config, location=BQ_LOCATION
    )
    load_job.result()
    table = client.get_table(table_id)
    print(f"  Loaded {table.num_rows} rows into {table_id}")


def main():
    print("Config:")
    print(f"  GCP_PROJECT_ID = {GCP_PROJECT_ID}")
    print(f"  GCS_BUCKET     = {GCS_BUCKET}")
    print(f"  BQ_DATASET     = {BQ_DATASET}")
    print(f"  BQ_LOCATION    = {BQ_LOCATION}")
    print(f"  DATA_DIR       = {DATA_DIR}")
    print()

    for taxi_type in TAXI_TYPES:
        print(f"--- {taxi_type} taxi ---")
        parquet_paths = download_and_convert(taxi_type)
        if not parquet_paths:
            print(f"  No parquet files for {taxi_type}; skipping.")
            continue
        gcs_prefix = f"taxi_rides_ny/{taxi_type}"
        uris = upload_to_gcs(parquet_paths, gcs_prefix)
        load_bigquery_table(taxi_type, uris)
        print()

    print("Done. Tables ready: nytaxi.green_tripdata, nytaxi.yellow_tripdata")
    print("Next: run dbt build --target prod in dbt Cloud, then run the HW4 notebook.")


if __name__ == "__main__":
    main()
    sys.exit(0)
