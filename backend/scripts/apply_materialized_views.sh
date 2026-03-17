#!/usr/bin/env bash
set -euo pipefail

# Root directory (backend/)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load .env if present
if [[ -f "$ROOT_DIR/.env" ]]; then
  export $(grep -v '^#' "$ROOT_DIR/.env" | xargs)
fi

: "${DB_HOST:=localhost}"
: "${DB_PORT:=5432}"
: "${DB_NAME:=meteodb}"
: "${DB_USER:=infoclimat}"
: "${DB_PASSWORD:=}"

export PGPASSWORD="$DB_PASSWORD"

MATVIEWS_DIR="${ROOT_DIR}/sql/materialized_views"

if [[ ! -d "$MATVIEWS_DIR" ]]; then
  echo "ERROR: materialized views directory not found: $MATVIEWS_DIR" >&2
  exit 1
fi

shopt -s nullglob
files=("$MATVIEWS_DIR"/*.sql)
shopt -u nullglob

if [[ ${#files[@]} -eq 0 ]]; then
  echo "ERROR: no .sql files found in $MATVIEWS_DIR" >&2
  exit 1
fi

for f in "${files[@]}"; do
  echo "Applying materialized view $(basename "$f")"
  psql -h "$DB_HOST" \
       -p "$DB_PORT" \
       -U "$DB_USER" \
       -d "$DB_NAME" \
       -v ON_ERROR_STOP=1 \
       -f "$f"
done

echo "Sanity checks:"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<'SQL'
SELECT COUNT(*) AS baseline_station_daily_mean_1991_2020_count
FROM public.baseline_station_daily_mean_1991_2020;

SELECT *
FROM public.baseline_station_daily_mean_1991_2020
LIMIT 5;
SQL

echo "Materialized views applied."oui
