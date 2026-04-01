#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

: "${DB_HOST:?DB_HOST is required}"
: "${DB_PORT:?DB_PORT is required}"
: "${DB_NAME:?DB_NAME is required}"
: "${DB_USER:?DB_USER is required}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"

export PGPASSWORD="${DB_PASSWORD}"

MV_SQL="${ROOT_DIR}/sql/materialized_views/records/001_mv_records_absolus.sql"

[[ -f "${MV_SQL}" ]] || { echo "Missing file: ${MV_SQL}" >&2; exit 1; }

echo "Creating mv_records_absolus..."
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" \
     -v ON_ERROR_STOP=1 \
     -f "${MV_SQL}"

echo "Sanity check:"
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" <<'SQL'
SELECT period_type, period_value, record_type, COUNT(*) AS nb_records
FROM public.mv_records_absolus
GROUP BY period_type, period_value, record_type
ORDER BY period_type, period_value, record_type
LIMIT 20;
SQL

echo "mv_records_absolus created."
