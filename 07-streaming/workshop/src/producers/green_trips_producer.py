"""
Homework: send green taxi October 2025 data to Redpanda topic `green-trips`.

Run from repo root or workshop with conda env that has kafka-python, pandas, pyarrow:
  python src/producers/green_trips_producer.py

Requires Redpanda on localhost:9092 and topic `green-trips` created.
"""

import json
import math
from time import time

import pandas as pd
from kafka import KafkaProducer

URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-10.parquet"
COLUMNS = [
    "lpep_pickup_datetime",
    "lpep_dropoff_datetime",
    "PULocationID",
    "DOLocationID",
    "passenger_count",
    "trip_distance",
    "tip_amount",
    "total_amount",
]


def _json_safe(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return value


def row_to_dict(row) -> dict:
    return {c: _json_safe(row[c]) for c in COLUMNS}


def value_serializer(obj: dict) -> bytes:
    return json.dumps(obj, separators=(",", ":")).encode("utf-8")


def main():
    df = pd.read_parquet(URL, columns=COLUMNS)
    server = "localhost:9092"
    topic_name = "green-trips"
    producer = KafkaProducer(
        bootstrap_servers=[server],
        value_serializer=lambda v: value_serializer(v),
    )
    t0 = time()
    for _, row in df.iterrows():
        producer.send(topic_name, value=row_to_dict(row))
    producer.flush()
    t1 = time()
    print(f"took {(t1 - t0):.2f} seconds")


if __name__ == "__main__":
    main()
