#!/usr/bin/env bash
set -euo pipefail

# Root directory (backend/)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"


: "${DB_HOST:?DB_HOST is required}"
: "${DB_PORT:?DB_PORT is required}"
: "${DB_NAME:?DB_NAME is required}"
: "${DB_USER:?DB_USER is required}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"

export PGPASSWORD="$DB_PASSWORD"

VIEWS_DIR="${ROOT_DIR}/sql/views"
V_QUOTIDIENNE_REALTIME_SQL="${ROOT_DIR}/sql/materialized_views/300_001_v_quotidienne_realtime.sql"
MV_QUOTIDIENNE_REALTIME_SQL="${ROOT_DIR}/sql/materialized_views/301_001_mv_quotidienne_realtime.sql"
V_FIRST_TEMPERATURE_DATE_SQL="${ROOT_DIR}/sql/materialized_views/100_002_v_first_temperature_date.sql"
MV_FIRST_TEMPERATURE_DATE_SQL="${ROOT_DIR}/sql/materialized_views/101_002_mv_first_temperature_date.sql"

apply_sql_file() {
  local sql_path="$1"

  if [[ ! -f "$sql_path" ]]; then
    echo "ERROR: SQL file not found: ${sql_path}" >&2
    exit 1
  fi

  echo "Applying $(basename "$sql_path")"
  psql -h "$DB_HOST" \
     -p "$DB_PORT" \
     -U "$DB_USER" \
     -d "$DB_NAME" \
     -v ON_ERROR_STOP=1 \
     -f "$sql_path"
}

if [[ ! -d "$VIEWS_DIR" ]]; then
  echo "ERROR: views directory not found: ${VIEWS_DIR}" >&2
  exit 1
fi

apply_sql_file "$V_QUOTIDIENNE_REALTIME_SQL"
apply_sql_file "$MV_QUOTIDIENNE_REALTIME_SQL"
apply_sql_file "$V_FIRST_TEMPERATURE_DATE_SQL"
apply_sql_file "$MV_FIRST_TEMPERATURE_DATE_SQL"

for f in "${VIEWS_DIR}"/*.sql; do
  apply_sql_file "$f"
done

echo "Sanity checks:"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<'SQL'
SELECT COUNT(*) AS v_station_count FROM public.v_station_qualifiee_hexagone;
SELECT COUNT(*) AS v_quotidienne_itn_count FROM public.v_quotidienne;
SQL

echo "Views applied."
