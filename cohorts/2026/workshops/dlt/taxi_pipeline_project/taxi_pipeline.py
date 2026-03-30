
import requests
import dlt

BASE_URL = "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api"
DUCKDB_PATH = r"/Users/sahand/Desktop/DataTalks/DataEngineering2025/data-engineering-zoomcamp/cohorts/2026/workshops/dlt/taxi_pipeline_project/taxi_pipeline.duckdb"


def fetch_pages(page_size: int = 1000):
    page = 1
    while True:
        response = requests.get(
            BASE_URL,
            params={"page": page, "page_size": page_size},
            timeout=30,
        )
        response.raise_for_status()
        rows = response.json()
        if not rows:
            break
        yield from rows
        page += 1


@dlt.resource(name="ny_taxi")
def ny_taxi_resource():
    yield from fetch_pages(page_size=1000)


def run():
    pipeline = dlt.pipeline(
        pipeline_name="taxi_pipeline",
        destination=dlt.destinations.duckdb(DUCKDB_PATH),
        dataset_name="taxi_data",
    )
    load_info = pipeline.run(ny_taxi_resource(), write_disposition="replace")
    print(load_info)


if __name__ == "__main__":
    run()
