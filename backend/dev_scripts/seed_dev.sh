#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

: "${DB_HOST:?DB_HOST is required}"
: "${DB_PORT:?DB_PORT is required}"
: "${DB_NAME:?DB_NAME is required}"
: "${DB_USER:?DB_USER is required}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"

export PGPASSWORD="${DB_PASSWORD}"

psql_base=(psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -v ON_ERROR_STOP=1)

SCHEMA_SQL="${ROOT_DIR}/sql/schemas/001_source_tables.sql"
STATION_SQL="${ROOT_DIR}/db_data/station.sql"
QUOTIDIENNE_CSV="${ROOT_DIR}/db_data/quotidienne_2024_2025.csv"
ITN_BASELINE_CSV="${ROOT_DIR}/db_data/itn_baseline_9120.csv"
STATION_BASELINE_CSV="${ROOT_DIR}/db_data/baseline_stations_daily_mean_9120.csv"
ITN_BASELINE_MONTHLY_CSV="${ROOT_DIR}/db_data/itn_baseline_monthly_9120.csv"
ITN_BASELINE_YEARLY_CSV="${ROOT_DIR}/db_data/itn_baseline_yearly_9120.csv"

for f in \
  "${SCHEMA_SQL}" \
  "${STATION_SQL}" \
  "${QUOTIDIENNE_CSV}" \
  "${ITN_BASELINE_CSV}" \
  "${ITN_BASELINE_MONTHLY_CSV}" \
  "${ITN_BASELINE_YEARLY_CSV}" \
  "${STATION_BASELINE_CSV}"
do
  [[ -f "${f}" ]] || { echo "Missing file: ${f}" >&2; exit 1; }
done


echo "== Reset schema public =="
"${psql_base[@]}" <<'SQL'
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO public;
GRANT ALL ON SCHEMA public TO CURRENT_USER;
SQL

echo "== Create tables (schema) =="
"${psql_base[@]}" -f "$SCHEMA_SQL"

echo "== Import Station (SQL dump) =="
"${psql_base[@]}" -f "$STATION_SQL"

echo "== Import Quotidienne (CSV) =="
"${psql_base[@]}" -c "\copy public.\"Quotidienne\" FROM '${QUOTIDIENNE_CSV}' WITH (FORMAT csv, HEADER true)"

echo "== Apply views =="
bash "${ROOT_DIR}/dev_scripts/apply_views.sh"

echo "== Seed station baseline (dev CSV) =="
bash "${ROOT_DIR}/dev_scripts/seed_station_baseline.sh"

echo "== Seed ITN baseline (dev CSV) =="
bash "${ROOT_DIR}/dev_scripts/seed_itn_baseline.sh"

echo "== Seed ITN monthly baseline (dev CSV) =="
bash "${ROOT_DIR}/dev_scripts/seed_itn_baseline_monthly.sh"

echo "== Seed ITN yearly baseline (dev CSV) =="
bash "${ROOT_DIR}/dev_scripts/seed_itn_baseline_yearly.sh"

echo "== Sanity checks =="
"${psql_base[@]}" -c 'SELECT COUNT(*) AS station_count FROM public."Station";'
"${psql_base[@]}" -c 'SELECT COUNT(*) AS quotidienne_count FROM public."Quotidienne";'
"${psql_base[@]}" -c 'SELECT COUNT(*) AS v_station_count FROM public.v_station;'
"${psql_base[@]}" -c 'SELECT COUNT(*) AS v_quotidienne_itn_count FROM public.v_quotidienne_itn;'
"${psql_base[@]}" -c 'SELECT MIN(date), MAX(date) FROM public.v_quotidienne_itn;'
"${psql_base[@]}" -c 'SELECT COUNT(*) AS baseline_station_daily_mean_1991_2020_count FROM public.baseline_station_daily_mean_1991_2020;'
"${psql_base[@]}" -c 'SELECT * FROM public.baseline_station_daily_mean_1991_2020 ORDER BY station_code, month, day LIMIT 5;'
"${psql_base[@]}" -c 'SELECT COUNT(*) AS itn_baseline_count FROM public.mv_itn_baseline_1991_2020;'
"${psql_base[@]}" -c 'SELECT COUNT(*) AS itn_baseline_monthly_count FROM public.mv_itn_baseline_monthly_1991_2020;'
"${psql_base[@]}" -c 'SELECT COUNT(*) AS itn_baseline_yearly_count FROM public.mv_itn_baseline_yearly_1991_2020;'
"${psql_base[@]}" -c 'SELECT * FROM public.mv_itn_baseline_monthly_1991_2020 ORDER BY month LIMIT 5;'
"${psql_base[@]}" -c 'SELECT * FROM public.mv_itn_baseline_yearly_1991_2020;'

echo "Seed done."
