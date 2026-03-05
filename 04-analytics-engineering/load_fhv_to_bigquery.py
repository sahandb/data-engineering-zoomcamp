#!/usr/bin/env python3
"""
Load FHV (For-Hire Vehicle) trip data 2019 from DataTalksClub into BigQuery.
For HW4 Q6: creates nytaxi.fhv_tripdata so dbt stg_fhv_tripdata can read it.

Usage:
  export GCP_PROJECT_ID=... GCS_BUCKET=... BQ_DATASET=nytaxi BQ_LOCATION=US
  python load_fhv_to_bigquery.py
"""

import os
from pathlib import Path

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "project-3a3cf597-6dcd-4db6-8c0")
GCS_BUCKET = os.environ.get("GCS_BUCKET", "dezoomcamp-hw3-3a3cf597")
BQ_DATASET = os.environ.get("BQ_DATASET", "nytaxi")
BQ_LOCATION = os.environ.get("BQ_LOCATION", "US")
DATA_DIR = Path(os.environ.get("DATA_DIR", "data_fhv_2019"))

BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv"
MONTHS = list(range(1, 13))


def download_and_convert() -> list[Path]:
    import requests
    import duckdb

    data_dir = DATA_DIR
    data_dir.mkdir(parents=True, exist_ok=True)
    parquet_paths = []

    for month in MONTHS:
        csv_gz_name = f"fhv_tripdata_2019-{month:02d}.csv.gz"
        parquet_name = f"fhv_tripdata_2019-{month:02d}.parquet"
        parquet_path = data_dir / parquet_name
        csv_gz_path = data_dir / csv_gz_name

        if parquet_path.exists():
            print(f"  Skip (exists): {parquet_name}")
            parquet_paths.append(parquet_path)
            continue

        url = f"{BASE_URL}/{csv_gz_name}"
        try:
            print(f"  Downloading {csv_gz_name}...")
            resp = requests.get(url, stream=True, timeout=180)
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
            # Cast SR_Flag to INTEGER so all parquet files have same type for BigQuery
            try:
                con.execute(f"""
                    COPY (
                        SELECT * REPLACE(TRY_CAST("SR_Flag" AS INTEGER) AS "SR_Flag")
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
    from google.cloud import storage

    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    client = storage.Client.from_service_account_json(creds, project=GCP_PROJECT_ID) if creds and os.path.isfile(creds) else storage.Client(project=GCP_PROJECT_ID)
    bucket = client.bucket(GCS_BUCKET)
    uris = []
    for p in parquet_paths:
        blob_name = f"{gcs_prefix}/{p.name}"
        bucket.blob(blob_name).upload_from_filename(str(p), content_type="application/octet-stream")
        uris.append(f"gs://{GCS_BUCKET}/{blob_name}")
        print(f"  Uploaded {p.name}")
    return uris


def load_bigquery(source_uris: list[str]) -> None:
    from google.cloud import bigquery

    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    client = bigquery.Client.from_service_account_json(creds, project=GCP_PROJECT_ID) if creds and os.path.isfile(creds) else bigquery.Client(project=GCP_PROJECT_ID)
    table_id = f"{GCP_PROJECT_ID}.{BQ_DATASET}.fhv_tripdata"
    job_config = bigquery.LoadJobConfig(source_format=bigquery.SourceFormat.PARQUET, write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)
    print(f"  Loading {len(source_uris)} files into {table_id}...")
    load_job = client.load_table_from_uri(source_uris, table_id, job_config=job_config, location=BQ_LOCATION)
    load_job.result()
    t = client.get_table(table_id)
    print(f"  Loaded {t.num_rows} rows into {table_id}")


def main():
    print("Config: GCP_PROJECT_ID=%s GCS_BUCKET=%s BQ_DATASET=%s" % (GCP_PROJECT_ID, GCS_BUCKET, BQ_DATASET))
    print("--- FHV 2019 ---")
    paths = download_and_convert()
    if not paths:
        print("No parquet files; exiting.")
        return
    uris = upload_to_gcs(paths, "taxi_rides_ny/fhv")
    load_bigquery(uris)
    print("Done. Table nytaxi.fhv_tripdata ready. Run: dbt run --select stg_fhv_tripdata --target prod")


if __name__ == "__main__":
    main()
