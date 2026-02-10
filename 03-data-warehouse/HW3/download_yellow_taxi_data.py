"""
Download Yellow Taxi parquet files (Jan–Jun 2024) to a local directory.
No GCS credentials needed. Use these files for local DuckDB or then upload via load_yellow_taxi_data.py.
"""
import os
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-"
MONTHS = [f"{i:02d}" for i in range(1, 7)]
DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "data")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_file(month):
    url = f"{BASE_URL}{month}.parquet"
    file_path = os.path.join(DOWNLOAD_DIR, f"yellow_tripdata_2024-{month}.parquet")
    try:
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, file_path)
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        print(f"Downloaded: {file_path} ({size_mb:.1f} MB)")
        return file_path
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=4) as executor:
        paths = list(executor.map(download_file, MONTHS))
    ok = sum(1 for p in paths if p is not None)
    print(f"Done. {ok}/6 files in {os.path.abspath(DOWNLOAD_DIR)}")
