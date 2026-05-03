#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

: "${DB_HOST:?DB_HOST is required}"
: "${DB_PORT:?DB_PORT is required}"
: "${DB_NAME:?DB_NAME is required}"
: "${DB_USER:?DB_USER is required}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"

export PGPASSWORD="${DB_PASSWORD}"


MV_SQL_COMPLETNESS_PAR_STATION="${ROOT_DIR}/sql/materialized_views/completeness/001_mv_completeness_par_station_classe_4_1806_2026.sql"

MV_SQL_COMPLETNESS_PAR_STATION_ET_CLASSE="${ROOT_DIR}/sql/materialized_views/completeness/002_mv_completeness_par_station_et_classe_1806_2026.sql"

[[ -f "${MV_SQL_COMPLETNESS_PAR_STATION}" ]] ||
{ echo "Missing file: ${MV_SQL_COMPLETNESS_PAR_STATION}" >&2; exit 1; }

[[ -f "${MV_SQL_COMPLETNESS_PAR_STATION_ET_CLASSE}" ]] ||
{ echo "Missing file: ${MV_SQL_COMPLETNESS_PAR_STATION_ET_CLASSE}" >&2; exit 1; }

echo "Creating mv_completeness par station..."
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" \
     -v ON_ERROR_STOP=1 \
     -f "${MV_SQL_COMPLETNESS_PAR_STATION}"

echo "Creating mv_completeness par station et classe..."
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" \
     -v ON_ERROR_STOP=1 \
     -f "${MV_SQL_COMPLETNESS_PAR_STATION_ET_CLASSE}"


echo "Sanity checks:"
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" <<'SQL'
SELECT COUNT(*) AS station_completeness_count FROM mv_completeness_par_station_classe_4_1806_2026;
SELECT COUNT(*) AS station_completeness_count FROM mv_completeness_par_station_classe_1806_2026;
SQL

echo "mv completeness created."
