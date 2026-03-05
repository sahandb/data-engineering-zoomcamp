# HW4 Step-by-Step: Load Data, Run dbt, Run the Notebook

This guide gets you from zero to running the HW4 notebook with real answers on **BigQuery** (Cloud setup).

---

## What you need before starting

- **GCP project** (e.g. `project-3a3cf597-6dcd-4db6-8c0`) with billing enabled  
- **BigQuery** dataset `nytaxi` (from Module 3) in your project  
- **GCS bucket** in the same project (e.g. `dezoomcamp-hw3-3a3cf597` or `bucket_taxi_data`)  
- **Credentials:** service account JSON with BigQuery + Storage permissions, or `gcloud auth application-default login`  
- **dbt Cloud** account (optional) — or use **dbt Core locally** with BigQuery (see Step 4 alternative below)  
- **Conda** env `dataTalks` (or any Python 3.10+ with the packages below)

---

## Step 1: Install Python dependencies

In a terminal, activate your environment and install:

```bash
conda activate dataTalks
pip install google-cloud-bigquery google-cloud-storage requests duckdb pandas
```

---

## Step 2: Set environment variables

Use your real GCP project ID and bucket name. Dataset should be `nytaxi` (so dbt finds the tables).  
If your BigQuery dataset is in a region like `us-central1`, set `BQ_LOCATION` to match.

```bash
export GCP_PROJECT_ID="project-3a3cf597-6dcd-4db6-8c0"
export GCS_BUCKET="dezoomcamp-hw3-3a3cf597"
export BQ_DATASET="nytaxi"
export BQ_LOCATION="US"

# If you use a service account JSON key:
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account.json"
```

(Optional) To use a different bucket or dataset, change `GCS_BUCKET` / `BQ_DATASET`. The script defaults match the values above.

---

## Step 3: Run the load script

From the **repo root** (or from `04-analytics-engineering/`):

```bash
cd /Users/sahand/Desktop/DataTalks/DataEngineering2025/data-engineering-zoomcamp/04-analytics-engineering
python load_taxi_data_to_bigquery.py
```

What it does:

1. **Downloads** green and yellow taxi CSV.gz files for 2019 and 2020 from the [DataTalksClub NYC TLC releases](https://github.com/DataTalksClub/nyc-tlc-data/releases) (required for correct homework answers).
2. **Converts** each file to Parquet and saves under `data_taxi_2019_2020/yellow/` and `data_taxi_2019_2020/green/`.
3. **Uploads** Parquet files to GCS under `gs://YOUR_BUCKET/taxi_rides_ny/yellow/` and `.../green/`.
4. **Loads** into BigQuery:
   - `nytaxi.green_tripdata` (all green 2019–2020)
   - `nytaxi.yellow_tripdata` (all yellow 2019–2020)

This can take **30–60+ minutes** (download + convert + upload + load). You can re-run the script later; it skips files that already exist locally.

When it finishes, you should see in BigQuery (Console → Explorer → `nytaxi`):

- `green_tripdata`
- `yellow_tripdata`

---

## Step 4: Run dbt (choose one)

### Option A — Run dbt **locally** with BigQuery (no dbt Cloud)

1. **Install dbt BigQuery adapter** (once):
   ```bash
   conda activate dataTalks
   pip install dbt-bigquery
   ```

2. **Profile** — A `~/.dbt/profiles.yml` is already set up for project `taxi_rides_ny` with BigQuery. It uses env vars for project and credentials.

3. **One-time auth** (use your Google account):
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

4. **Set project and run** (from any terminal where you’ll run dbt):
   ```bash
   conda activate dataTalks
   export GCP_PROJECT_ID="project-3a3cf597-6dcd-4db6-8c0"
   cd 04-analytics-engineering/taxi_rides_ny
   dbt build --target prod
   ```
   Or use the helper script (after setting `GCP_PROJECT_ID`):
   ```bash
   conda activate dataTalks
   export GCP_PROJECT_ID="project-3a3cf597-6dcd-4db6-8c0"
   cd 04-analytics-engineering/taxi_rides_ny
   ./run_dbt_prod.sh
   ```

5. After it succeeds, in BigQuery you’ll see datasets like `dbt_prod_staging`, `dbt_prod_marts`, and the table `fct_monthly_zone_revenue`. Use those exact dataset names in the HW4 notebook (Step 6).

### Option B — Set up dbt Cloud and connect to BigQuery

1. Go to [dbt Cloud](https://cloud.getdbt.com/) and sign in (or create a free account).
2. **Create a new project** (or use an existing one):
   - Name: e.g. `taxi_rides_ny`
3. **Connect BigQuery:**
   - Choose **BigQuery** as the warehouse.
   - Upload your **service account JSON** (same one you use for `GOOGLE_APPLICATION_CREDENTIALS`).
   - **Dataset:** e.g. `dbt_prod` (dbt will create `dbt_prod_staging`, `dbt_prod_marts`, etc.).
   - **Location:** same as your `nytaxi` dataset (e.g. `US` or `us-central1`).
   - Test the connection and continue.
4. **Connect the repo:**
   - Either “Let dbt manage the repository” and then copy the `taxi_rides_ny` dbt project into it, or connect your GitHub repo that contains `04-analytics-engineering/taxi_rides_ny/`.
5. **Set environment variable in dbt Cloud:**
   - In the project settings, set **Environment variable** `GCP_PROJECT_ID` = your GCP project ID (e.g. `project-3a3cf597-6dcd-4db6-8c0`).  
   The dbt `sources.yml` uses this so sources point to `GCP_PROJECT_ID.nytaxi.green_tripdata` and `yellow_tripdata`.

Details and screenshots: [Cloud Setup Guide](../setup/cloud_setup.md).

---

## Step 5: Run dbt in production (if using dbt Cloud)

In dbt Cloud:

1. Open your project and go to the **IDE** or **Deploy**.
2. Run a **production** job (or in the IDE run with **target = prod**):
   ```bash
   dbt build --target prod
   ```
3. Wait for the run to finish. Then in **BigQuery → Explorer** you should see new datasets, for example:
   - `dbt_prod_staging`
   - `dbt_prod_intermediate`
   - `dbt_prod_marts` (and possibly sub-schemas like `dbt_prod_marts_reporting`)

4. **Note the exact dataset name** where `fct_monthly_zone_revenue` lives (e.g. `dbt_prod_marts` or `dbt_prod_marts_reporting`). You’ll need it for the notebook.

---

## Step 6: Run the HW4 notebook

1. Open **`04-analytics-engineering/HW4/hw4.ipynb`** in Cursor (or Jupyter).
2. Select the **dataTalks** kernel (or the env where you installed `google-cloud-bigquery` and `pandas`).
3. In the **config cell** (second code cell), set:
   - `PROJECT` = your GCP project ID (e.g. `project-3a3cf597-6dcd-4db6-8c0`)
   - `MARTS_DATASET` = the dataset that contains `fct_monthly_zone_revenue` (e.g. `dbt_prod_marts` or `dbt_prod_marts_reporting`)
   - `STAGING_DATASET` = the dataset that contains staging models (e.g. `dbt_prod_staging`)
4. **Run All** (or run cells from top to bottom).

The notebook will:

- Answer Q1 and Q2 (theory).
- Run BigQuery queries for Q3–Q5 (record count, best zone for Green 2020, Green trips Oct 2019) and show the results.
- For Q6, run the count on `stg_fhv_tripdata` **after** you’ve loaded FHV 2019 data, added the source and staging model in dbt, and run `dbt run --select stg_fhv_tripdata --target prod`.

Use the printed numbers and zone names to fill the homework form.

---

## Question 6 (FHV) — optional

To get the **count of records in `stg_fhv_tripdata`** and submit Q6:

1. **Load FHV 2019 into BigQuery** (same env vars as Step 2; can use `gcloud auth application-default login` instead of a keyfile):
   ```bash
   conda activate dataTalks
   export GCP_PROJECT_ID="project-3a3cf597-6dcd-4db6-8c0"
   export GCS_BUCKET="dezoomcamp-hw3-3a3cf597"
   cd 04-analytics-engineering
   python load_fhv_to_bigquery.py
   ```
   This creates `nytaxi.fhv_tripdata`. It can take a while (12 months of FHV data).

2. **Run the FHV staging model** (sources and `stg_fhv_tripdata.sql` are already in the repo):
   ```bash
   export GCP_PROJECT_ID="project-3a3cf597-6dcd-4db6-8c0"
   cd 04-analytics-engineering/taxi_rides_ny
   dbt run --select stg_fhv_tripdata --target prod
   ```

3. **Run the Q6 cell** in `hw4.ipynb` (or re-run the notebook). The result is the count; choose the matching option: **42,084,899 | 43,244,693 | 22,998,722 | 44,112,187**.

---

## Quick reference

| Step | What you do |
|------|-------------|
| 1 | `pip install google-cloud-bigquery google-cloud-storage requests duckdb pandas` (and `dbt-bigquery` for local dbt) |
| 2 | `export GCP_PROJECT_ID=... GCS_BUCKET=... BQ_DATASET=nytaxi GOOGLE_APPLICATION_CREDENTIALS=...` |
| 3 | `python 04-analytics-engineering/load_taxi_data_to_bigquery.py` |
| 4 | **Local:** `gcloud auth login` + `gcloud auth application-default login` (once), then `export GCP_PROJECT_ID=...` and `cd taxi_rides_ny && dbt build --target prod` — or use dbt Cloud |
| 5 | (If dbt Cloud) Run prod job: `dbt build --target prod` |
| 6 | Open `HW4/hw4.ipynb`, set PROJECT / MARTS_DATASET / STAGING_DATASET, Run All |

---

## Troubleshooting

- **“Dataset … was not found”**  
  Make sure Step 5 completed and you’re using the **exact** dataset names from BigQuery in the notebook (`MARTS_DATASET`, `STAGING_DATASET`).

- **“Not found: Table … green_tripdata”**  
  Step 3 didn’t finish or wrote to another dataset. Check BigQuery for `nytaxi.green_tripdata` and `nytaxi.yellow_tripdata`.

- **Load script: download or convert errors**  
  Use data from the **DataTalksClub** releases only. If a single month fails, you can re-run; the script skips existing Parquet files.

- **dbt source freshness / wrong project**  
  In dbt Cloud, set the env var `GCP_PROJECT_ID` so `sources.yml` resolves to your project’s `nytaxi` dataset.
