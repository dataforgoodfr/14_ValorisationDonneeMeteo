#!/usr/bin/env bash
set -euo pipefail

# Root directory (backend/)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load .env if present
if [[ -f "$ROOT_DIR/.env" ]]; then
  export $(grep -v '^#' "${ROOT_DIR}/.env" | xargs)
fi

: "${DB_HOST:=localhost}"
: "${DB_PORT:=5432}"
: "${DB_NAME:=meteodb}"
: "${DB_USER:=infoclimat}"
: "${DB_PASSWORD:=}"

export PGPASSWORD="$DB_PASSWORD"

CSV_PATH="${1:-${ROOT_DIR}/db_data/itn_baseline_9120.csv}"
TABLE_NAME="${TABLE_NAME:-mv_itn_baseline_1991_2020}"

if [[ ! -f "$CSV_PATH" ]]; then
  echo "ERROR: CSV file not found: ${CSV_PATH}" >&2
  exit 1
fi

echo "Seeding ${TABLE_NAME} from ${CSV_PATH}"

# Vérifie que la table existe
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
    climatology_day integer PRIMARY KEY,
    month integer NOT NULL,
    day_of_month integer NOT NULL,
    sample_size integer NOT NULL,
    itn_mean double precision NOT NULL,
    itn_stddev double precision NOT NULL,
    itn_p20 double precision NOT NULL,
    itn_p80 double precision NOT NULL,
    CONSTRAINT uq_${TABLE_NAME}_month_day UNIQUE (month, day_of_month)
);
SQL
fi

# Vérifie les colonnes attendues
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

# Recharge complètement la table
psql -h "$DB_HOST" \
     -p "$DB_PORT" \
     -U "$DB_USER" \
     -d "$DB_NAME" \
     -v ON_ERROR_STOP=1 <<SQL
TRUNCATE TABLE public.${TABLE_NAME};
SQL

# Import CSV via \copy (côté client, donc pratique en dev)
psql -h "$DB_HOST" \
     -p "$DB_PORT" \
     -U "$DB_USER" \
     -d "$DB_NAME" \
     -v ON_ERROR_STOP=1 <<SQL
\copy public.${TABLE_NAME} (climatology_day, month, day_of_month, sample_size, itn_mean, itn_stddev, itn_p20, itn_p80) FROM '${CSV_PATH}' WITH (FORMAT csv, HEADER true)
SQL

echo "Sanity checks:"
psql -h "$DB_HOST" \
     -p "$DB_PORT" \
     -U "$DB_USER" \
     -d "$DB_NAME" <<SQL
SELECT COUNT(*) AS baseline_count
FROM public.${TABLE_NAME};

SELECT *
FROM public.${TABLE_NAME}
ORDER BY climatology_day
LIMIT 5;

SELECT *
FROM public.${TABLE_NAME}
ORDER BY climatology_day DESC
LIMIT 5;

SELECT COUNT(*) AS invalid_sample_size_count
FROM public.${TABLE_NAME}
WHERE sample_size <> 30;
SQL

echo "Baseline seed applied."
