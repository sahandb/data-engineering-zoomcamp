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

To run the pipeline once everything is configured:

```bash
cd my-pipeline
bruin run ./pipeline.yml
# Or, for a specific pipeline path, e.g.:
# bruin run ./pipelines/nyc-taxi/pipeline.yml
```

Useful flags:

- `--full-refresh` — drop and recreate tables (first-time run on empty DB)
- `--var 'taxi_types=["yellow"]'` — override variables
- `--asset <name> --downstream` — run one asset and its dependents
- `bruin lineage ./pipeline.yml` — view dependency graph

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

## Troubleshooting

- **“command not found: bruin”** — Ensure the install script added Bruin to your `PATH` (e.g. `~/.bruin/bin` or similar; see install output).
- **“Connection not found”** — Check that the connection name in your pipeline matches a connection in `.bruin.yml` for the chosen environment.
- **“Pipeline / asset not found”** — Run from the project root and use the correct path to `pipeline.yml` (e.g. `./pipeline.yml` or `./pipelines/nyc-taxi/pipeline.yml`).
- **First run on empty DuckDB** — Use `bruin run ./pipeline.yml --full-refresh` so tables are created from scratch.
