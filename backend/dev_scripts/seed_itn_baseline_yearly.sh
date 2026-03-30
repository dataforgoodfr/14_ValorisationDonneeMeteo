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

CSV_PATH="${1:-${ROOT_DIR}/db_data/itn_baseline_yearly_9120.csv}"
TABLE_NAME="${TABLE_NAME:-mv_itn_baseline_yearly_1991_2020}"
# Détecte si l’objet cible existe déjà et s’il s’agit d’une table ou d’une materialized view.
# En dev, cet objet peut avoir été créé comme une materialized view (comportement prod),
# mais on souhaite le remplacer par une table alimentée depuis un CSV.
# Catalogue PostgreSQL :
# - relkind = 'r' → table
# - relkind = 'm' → materialized view
if [[ ! -f "$CSV_PATH" ]]; then
  echo "ERROR: CSV file not found: ${CSV_PATH}" >&2
  exit 1
fi

psql -h "$DB_HOST" \
     -p "$DB_PORT" \
     -U "$DB_USER" \
     -d "$DB_NAME" \
     -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public'
          AND c.relname = '${TABLE_NAME}'
          AND c.relkind = 'm'
    ) THEN
        EXECUTE 'DROP MATERIALIZED VIEW public.${TABLE_NAME}';
    ELSIF EXISTS (
        SELECT 1
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public'
          AND c.relname = '${TABLE_NAME}'
          AND c.relkind = 'r'
    ) THEN
        EXECUTE 'DROP TABLE public.${TABLE_NAME}';
    END IF;
END
\$\$;
SQL

echo "Seeding ${TABLE_NAME} from ${CSV_PATH}"

psql -h "$DB_HOST" \
     -p "$DB_PORT" \
     -U "$DB_USER" \
     -d "$DB_NAME" \
     -v ON_ERROR_STOP=1 <<SQL
CREATE TABLE public.${TABLE_NAME} (
    sample_size integer NOT NULL,
    itn_mean double precision NOT NULL,
    itn_stddev double precision NOT NULL,
    itn_p20 double precision NOT NULL,
    itn_p80 double precision NOT NULL
);
SQL

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
     -v ON_ERROR_STOP=1 <<SQL
\copy public.${TABLE_NAME} (sample_size, itn_mean, itn_stddev, itn_p20, itn_p80) FROM '${CSV_PATH}' WITH (FORMAT csv, HEADER true)
SQL

echo "Sanity checks:"
psql -h "$DB_HOST" \
     -p "$DB_PORT" \
     -U "$DB_USER" \
     -d "$DB_NAME" <<SQL
SELECT COUNT(*) AS baseline_count
FROM public.${TABLE_NAME};

SELECT *
FROM public.${TABLE_NAME};

SELECT COUNT(*) AS invalid_sample_size_count
FROM public.${TABLE_NAME}
WHERE sample_size <> 30;
SQL

echo "Yearly baseline seed applied."
