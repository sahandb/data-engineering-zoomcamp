#!/usr/bin/env python3
"""Quick test of HW4 BigQuery queries using GCP project from load scripts."""
import os
import sys

# Use same defaults as load_taxi_data_to_bigquery.py
PROJECT = os.environ.get("GCP_PROJECT_ID", "project-3a3cf597-6dcd-4db6-8c0")
MARTS_DATASET = os.environ.get("MARTS_DATASET", "dbt_prod")
STAGING_DATASET = os.environ.get("STAGING_DATASET", "dbt_prod")

def main():
    try:
        from google.cloud import bigquery
    except ImportError:
        print("Install: pip install google-cloud-bigquery")
        sys.exit(1)
    client = bigquery.Client(project=PROJECT)
    ok = True

    # Q3: count fct_monthly_zone_revenue (expected 12184)
    sql3 = f"SELECT COUNT(*) AS n FROM `{PROJECT}.{MARTS_DATASET}.fct_monthly_zone_revenue`"
    try:
        row = next(client.query(sql3).result())
        n3 = row.n
        print(f"Q3 fct_monthly_zone_revenue count: {n3} (expected 12184)")
        if n3 != 12184:
            ok = False
    except Exception as e:
        print(f"Q3 FAIL: {e}")
        ok = False

    # Q4: best Green 2020 zone (expected East Harlem North)
    sql4 = f"""
    SELECT pickup_zone, SUM(revenue_monthly_total_amount) AS total
    FROM `{PROJECT}.{MARTS_DATASET}.fct_monthly_zone_revenue`
    WHERE service_type = 'Green' AND revenue_month >= '2020-01-01' AND revenue_month <= '2020-12-01'
    GROUP BY pickup_zone ORDER BY total DESC LIMIT 1
    """
    try:
        row = next(client.query(sql4).result())
        zone = row.pickup_zone
        print(f"Q4 best Green 2020 zone: {zone} (expected East Harlem North)")
        if zone != "East Harlem North":
            ok = False
    except Exception as e:
        print(f"Q4 FAIL: {e}")
        ok = False

    # Q5: Green trips Oct 2019 (expected 384624)
    sql5 = f"""
    SELECT SUM(total_monthly_trips) AS n
    FROM `{PROJECT}.{MARTS_DATASET}.fct_monthly_zone_revenue`
    WHERE service_type = 'Green' AND revenue_month = '2019-10-01'
    """
    try:
        row = next(client.query(sql5).result())
        n5 = row.n
        print(f"Q5 Green trips Oct 2019: {n5} (expected 384624)")
        if n5 != 384624:
            ok = False
    except Exception as e:
        print(f"Q5 FAIL: {e}")
        ok = False

    # Q6: count stg_fhv_tripdata (expected 43244693)
    sql6 = f"SELECT COUNT(*) AS n FROM `{PROJECT}.{STAGING_DATASET}.stg_fhv_tripdata`"
    try:
        row = next(client.query(sql6).result())
        n6 = row.n
        print(f"Q6 stg_fhv_tripdata count: {n6} (expected 43244693)")
        if n6 != 43244693:
            ok = False
    except Exception as e:
        print(f"Q6 FAIL: {e}")
        ok = False

    if ok:
        print("\nAll HW4 BigQuery checks passed.")
    else:
        print("\nSome checks did not match expected values.")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
