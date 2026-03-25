#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  source "$ROOT_DIR/.env"
  set +a
fi

: "${DB_HOST:=localhost}"
: "${DB_PORT:=5432}"
: "${DB_NAME:=meteodb}"
: "${DB_USER:=infoclimat}"
: "${DB_PASSWORD:=}"

export PGPASSWORD="$DB_PASSWORD"

CSV_PATH="${1:-${ROOT_DIR}/db_data/baseline_stations_daily_mean_9120.csv}"
TABLE_NAME="${TABLE_NAME:-baseline_station_daily_mean_1991_2020}"

[[ -f "$CSV_PATH" ]] || { echo "Missing CSV: $CSV_PATH" >&2; exit 1; }

echo "Seeding ${TABLE_NAME} from $(basename "$CSV_PATH")"

OBJECT_KIND=$(psql -h "$DB_HOST" \
                   -p "$DB_PORT" \
                   -U "$DB_USER" \
                   -d "$DB_NAME" \
                   -tAc "
SELECT CASE c.relkind
         WHEN 'r' THEN 'table'
         WHEN 'm' THEN 'materialized_view'
         ELSE c.relkind::text
       END
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relname = '${TABLE_NAME}'
LIMIT 1;")

if [[ "$OBJECT_KIND" == "materialized_view" ]]; then
  echo "Dropping materialized view public.${TABLE_NAME} to replace it with a seeded table..."
  psql -h "$DB_HOST" \
       -p "$DB_PORT" \
       -U "$DB_USER" \
       -d "$DB_NAME" \
       -v ON_ERROR_STOP=1 \
       -c "DROP MATERIALIZED VIEW IF EXISTS public.${TABLE_NAME};"
fi

TABLE_EXISTS=$(psql -h "$DB_HOST" \
                    -p "$DB_PORT" \
                    -U "$DB_USER" \
                    -d "$DB_NAME" \
                    -tAc "SELECT to_regclass('public.${TABLE_NAME}') IS NOT NULL;")

if [[ "$TABLE_EXISTS" != "t" ]]; then
  echo "Table ${TABLE_NAME} does not exist, creating it..."

  psql -h "$DB_HOST" \
       -p "$DB_PORT" \
       -U "$DB_USER" \
       -d "$DB_NAME" \
       -v ON_ERROR_STOP=1 <<SQL
CREATE TABLE public.${TABLE_NAME} (
    station_code text NOT NULL,
    month integer NOT NULL,
    day integer NOT NULL,
    sample_count integer NOT NULL,
    baseline_mean_tntxm numeric(10, 2) NOT NULL,
    CONSTRAINT pk_${TABLE_NAME}
        PRIMARY KEY (station_code, month, day)
);
SQL
fi

echo "Checking target schema..."
psql -h "$DB_HOST" \
     -p "$DB_PORT" \
     -U "$DB_USER" \
     -d "$DB_NAME" \
     -v ON_ERROR_STOP=1 <<SQL
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = '${TABLE_NAME}'
ORDER BY ordinal_position;
SQL

psql -h "$DB_HOST" \
     -p "$DB_PORT" \
     -U "$DB_USER" \
     -d "$DB_NAME" \
     -v ON_ERROR_STOP=1 \
     -c "TRUNCATE TABLE public.${TABLE_NAME};"

psql -h "$DB_HOST" \
     -p "$DB_PORT" \
     -U "$DB_USER" \
     -d "$DB_NAME" \
     -v ON_ERROR_STOP=1 <<SQL
\copy public.${TABLE_NAME} (station_code, month, day, sample_count, baseline_mean_tntxm) FROM '${CSV_PATH}' WITH (FORMAT csv, HEADER true)
SQL

echo "Sanity checks:"
psql -h "$DB_HOST" \
     -p "$DB_PORT" \
     -U "$DB_USER" \
     -d "$DB_NAME" <<SQL
SELECT COUNT(*) AS station_baseline_count
FROM public.${TABLE_NAME};

SELECT *
FROM public.${TABLE_NAME}
ORDER BY station_code, month, day
LIMIT 5;
SQL

echo "Station baseline seed applied."
