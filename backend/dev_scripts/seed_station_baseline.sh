#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

: "${DB_HOST:?DB_HOST is required}"
: "${DB_PORT:?DB_PORT is required}"
: "${DB_NAME:?DB_NAME is required}"
: "${DB_USER:?DB_USER is required}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"

export PGPASSWORD="$DB_PASSWORD"

CSV_PATH="${1:-${ROOT_DIR}/db_data/baseline_stations_daily_mean_9120.csv}"
TABLE_NAME="${TABLE_NAME:-baseline_station_daily_mean_1991_2020}"

[[ -f "${CSV_PATH}" ]] || { echo "Missing CSV: ${CSV_PATH}" >&2; exit 1; }

echo "Seeding ${TABLE_NAME} from ${CSV_PATH}"

# Détecte si l’objet cible existe déjà et s’il s’agit d’une table ou d’une materialized view.
# En dev, cet objet peut avoir été créé comme une materialized view (comportement prod),
# mais on souhaite le remplacer par une table alimentée depuis un CSV.
# Catalogue PostgreSQL :
# - relkind = 'r' → table
# - relkind = 'm' → materialized view

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

# On créé la table en dev - en prod c'est une Materialized View
# Comme on a pas les données en dev pour calculer la MV on créé une table, que l'on seed plus loin avec un csv"
echo "Creating table ${TABLE_NAME}..."

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

# Ici on seed la table (fausse MV) avec des données csv
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
