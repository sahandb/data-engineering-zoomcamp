#!/usr/bin/env bash
# Run dbt build --target prod locally (BigQuery).
# One-time auth: gcloud auth login && gcloud auth application-default login
# Then set: export GCP_PROJECT_ID="your-gcp-project-id"
# Run: ./run_dbt_prod.sh   or   bash run_dbt_prod.sh

set -e
if [[ -z "${GCP_PROJECT_ID}" ]]; then
  echo "Error: GCP_PROJECT_ID is not set. Example: export GCP_PROJECT_ID=project-3a3cf597-6dcd-4db6-8c0"
  exit 1
fi
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo "Running dbt build --target prod (BigQuery project=$GCP_PROJECT_ID)"
dbt build --target prod
