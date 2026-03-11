#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f "$ROOT_DIR/.env" ]]; then
  export $(grep -v '^[[:space:]]*#' "$ROOT_DIR/.env" | xargs)
fi

: "${DB_HOST:=localhost}"
: "${DB_PORT:=5432}"
: "${DB_NAME:=meteodb}"
: "${DB_USER:=infoclimat}"
: "${DB_PASSWORD:=}"

export PGPASSWORD="$DB_PASSWORD"

psql_base=(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1)

SCHEMA_SQL="$ROOT_DIR/sql/schemas/001_source_tables.sql"
STATION_SQL="$ROOT_DIR/db_data/station.sql"
QUOTIDIENNE_CSV="$ROOT_DIR/db_data/quotidienne_2024_2025.csv"

for f in "$SCHEMA_SQL" "$STATION_SQL" "$QUOTIDIENNE_CSV"; do
  [[ -f "$f" ]] || { echo "Missing file: $f" >&2; exit 1; }
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
"${psql_base[@]}" -c "\copy public.\"Quotidienne\" FROM '$QUOTIDIENNE_CSV' WITH (FORMAT csv, HEADER true)"

echo "== Apply views =="
bash "$ROOT_DIR/scripts/apply_views.sh"

echo "== Sanity checks =="
"${psql_base[@]}" -c 'SELECT COUNT(*) AS station_count FROM public."Station";'
"${psql_base[@]}" -c 'SELECT COUNT(*) AS quotidienne_count FROM public."Quotidienne";'
"${psql_base[@]}" -c 'SELECT COUNT(*) AS v_station_count FROM public.v_station;'
"${psql_base[@]}" -c 'SELECT COUNT(*) AS v_quotidienne_itn_count FROM public.v_quotidienne_itn;'
"${psql_base[@]}" -c 'SELECT MIN(date), MAX(date) FROM public.v_quotidienne_itn;'

echo "Seed done."
