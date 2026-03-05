# HW5 Step-by-Step: Bruin Setup and Homework

This guide gets you from zero to completing the Module 5 homework (Data Platforms with Bruin).

---

## What you need before starting

- **Bruin CLI** (install via Step 1)
- **DuckDB** (used as the warehouse in the zoomcamp template; no separate install required if using Bruin’s default)
- **Module README** and **notes** for reference: [05-data-platforms/README.md](../README.md) and [notes/](../notes/)

---

## Step 1: Install Bruin CLI

```bash
curl -LsSf https://getbruin.com/install/cli | sh
```

Verify:

```bash
bruin --version
```

---

## Step 2: Initialize the zoomcamp template

From the **repo root** or a directory where you want the pipeline project:

```bash
bruin init zoomcamp my-pipeline
cd my-pipeline
```

This creates a Bruin project with the zoomcamp template (NYC taxi pipeline structure).

---

## Step 3: Configure `.bruin.yml`

1. In the project root, create or edit `.bruin.yml`.
2. Add a **DuckDB connection** (and optionally other environments). Example:

```yaml
default_environment: default

environments:
  default:
    connections:
      duckdb:
        - name: duckdb-default
          path: duckdb.db
```

3. **Important:** `.bruin.yml` is typically in `.gitignore` so secrets stay local.

---

## Step 4: Follow the tutorial

Complete the tutorial in the [main module README](../README.md):

- [Bruin Data Engineering Zoomcamp Template](https://github.com/bruin-data/bruin/tree/main/templates/zoomcamp)

The template is TODO-based: run `bruin init zoomcamp my-pipeline` and fill in configuration and code as guided by inline comments. The [notes](../notes/) contain reference implementations.

After this, you should have a working NYC taxi data pipeline.

---

## Step 5: Run the pipeline (optional)

From **inside** `my-pipeline` (so Bruin finds `.bruin.yml`), or pass it explicitly:

```bash
cd 05-data-platforms/my-pipeline
export PATH="$HOME/.local/bin:$PATH"   # if bruin was just installed
bruin run ./pipeline --config-file .bruin.yml --full-refresh
```

- **First run / empty DB:** use `--full-refresh`.
- **Override variables:** `bruin run ./pipeline --config-file .bruin.yml --var 'taxi_types=["yellow"]'`.
- **Run one asset + downstream:** `bruin run ./pipeline/assets/ingestion/trips.py --downstream --config-file .bruin.yml`.
- **View dependency graph (Q6):** `bruin lineage ./pipeline/assets/ingestion/trips.py`.

---

## Step 6: Open the homework notebook

1. Open `05-data-platforms/HW5/hw5.ipynb` in Jupyter or Cursor.
2. Run the cells to review the questions and answers (no BigQuery or external services required for the theory questions).
3. Use the answers to submit: <https://courses.datatalks.club/de-zoomcamp-2026/homework/hw5>

---

## Quick reference

| Step | What you do |
|------|-------------|
| 1 | `curl -LsSf https://getbruin.com/install/cli \| sh` |
| 2 | `bruin init zoomcamp my-pipeline` and `cd my-pipeline` |
| 3 | Configure `.bruin.yml` with DuckDB (or other) connection |
| 4 | Follow [module README](../README.md) and zoomcamp template tutorial |
| 5 | `bruin run ./pipeline.yml` (use `--full-refresh` on first run) |
| 6 | Open `HW5/hw5.ipynb`, review answers, submit at the homework form |

---

## Homework answers (reference)

| Question | Answer |
|----------|--------|
| Q1. Required files/directories | `.bruin.yml` and `pipeline/` with `pipeline.yml` and `assets/` |
| Q2. Best strategy for interval delete/insert | `time_interval` |
| Q3. Override array variable | `bruin run --var 'taxi_types=["yellow"]'` |
| Q4. Run asset + downstream | `bruin run ingestion/trips.py --downstream` |
| Q5. No NULLs on column | `name: not_null` |
| Q6. Visualize dependency graph | `bruin lineage` |
| Q7. First-time run, create tables from scratch | `--full-refresh` |

---

## How to fix HW5

**Setup / Bruin not working**

1. **Install Bruin CLI** (if missing): `curl -LsSf https://getbruin.com/install/cli | sh` then restart the terminal. Check: `bruin --version`.
2. **Init the project**: From a clean folder run `bruin init zoomcamp my-pipeline` and `cd my-pipeline`. The zoomcamp template must be used (homework expects it).
3. **Configure `.bruin.yml`** in the project root with a DuckDB connection (see Step 3 above). Without this, `bruin run` will fail.
4. **Run from the right place**: Run `bruin run` (or `bruin run ./pipeline.yml`) from inside `my-pipeline`, or pass the full path to the pipeline/asset.

**Wrong answer on the submission form**

Use the **exact option text** from the homework (the form is multiple choice):

| Q | Choose this option |
|---|--------------------|
| 1 | `.bruin.yml` and `pipeline/` with `pipeline.yml` and `assets/` |
| 2 | `time_interval` - incremental based on a time column |
| 3 | `bruin run --var 'taxi_types=["yellow"]'` |
| 4 | `bruin run ingestion/trips.py --downstream` |
| 5 | `name: not_null` |
| 6 | `bruin lineage` |
| 7 | `--full-refresh` |

**Notebook or paths**

- The notebook (`hw5.ipynb`) only has theory; no code to run. Open it and run cells to review.
- If a link is broken, the homework lives in `cohorts/2026/05-data-platforms/homework.md` and the form is: <https://courses.datatalks.club/de-zoomcamp-2026/homework/hw5>.

---

## Troubleshooting

- **“command not found: bruin”** — Ensure the install script added Bruin to your `PATH` (e.g. `~/.bruin/bin` or similar; see install output).
- **“Connection not found”** — Check that the connection name in your pipeline matches a connection in `.bruin.yml` for the chosen environment.
- **“Pipeline / asset not found”** — Run from the project root and use the correct path to `pipeline.yml` (e.g. `./pipeline.yml` or `./pipelines/nyc-taxi/pipeline.yml`).
- **First run on empty DuckDB** — Use `bruin run ./pipeline.yml --full-refresh` so tables are created from scratch.
