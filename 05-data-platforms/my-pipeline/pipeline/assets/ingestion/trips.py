"""@bruin

name: ingestion.trips
type: python
image: python:3.11
connection: duckdb-default
materialization:
  type: table
  strategy: append
columns:
  - name: pickup_datetime
    type: timestamp
    description: Pickup time
  - name: dropoff_datetime
    type: timestamp
    description: Dropoff time
  - name: fare_amount
    type: double
    description: Fare amount

@bruin"""

import pandas as pd
from datetime import datetime

def materialize():
    """Minimal ingestion: one placeholder row so table is created (for validate/run)."""
    return pd.DataFrame([{
        "pickup_datetime": pd.Timestamp("2019-01-01"),
        "dropoff_datetime": pd.Timestamp("2019-01-01"),
        "fare_amount": 0.0,
    }])


