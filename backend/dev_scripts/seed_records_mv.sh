#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ---------------------------------------------------------------------------
# Usage: seed_records_mv.sh [--cutoff YYYY-MM-DD]
#
#   --cutoff YYYY-MM-DD  Cutoff date à stocker dans mv_records_battus_meta.
#                        Par défaut : MAX(AAAAMMJJ) dans Quotidienne.
# ---------------------------------------------------------------------------
CUTOFF_ARG=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --cutoff)
            CUTOFF_ARG="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1" >&2
            echo "Usage: $0 [--cutoff YYYY-MM-DD]" >&2
            exit 1
            ;;
    esac
done

if [[ -n "${CUTOFF_ARG}" ]]; then
    if ! [[ "${CUTOFF_ARG}" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        echo "Invalid cutoff date '${CUTOFF_ARG}': expected YYYY-MM-DD" >&2
        exit 1
    fi
fi

: "${DB_HOST:?DB_HOST is required}"
: "${DB_PORT:?DB_PORT is required}"
: "${DB_NAME:?DB_NAME is required}"
: "${DB_USER:?DB_USER is required}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"

export PGPASSWORD="${DB_PASSWORD}"

MV_SQL="${ROOT_DIR}/sql/materialized_views/records/001_mv_records_battus.sql"

[[ -f "${MV_SQL}" ]] || { echo "Missing file: ${MV_SQL}" >&2; exit 1; }

echo "Creating mv_records_battus..."
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" \
     -v ON_ERROR_STOP=1 \
     -f "${MV_SQL}"

echo "Sanity check:"
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" <<'SQL'
SELECT period_type, period_value, record_type, COUNT(*) AS nb_records
FROM public.mv_records_battus
GROUP BY period_type, period_value, record_type
ORDER BY period_type, period_value, record_type
LIMIT 20;
SQL

echo "mv_records_battus created."

META_SQL="${ROOT_DIR}/sql/schemas/records/001_mv_records_battus_meta.sql"

[[ -f "${META_SQL}" ]] || { echo "Missing file: ${META_SQL}" >&2; exit 1; }

echo "Creating mv_records_battus_meta..."
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" \
     -v ON_ERROR_STOP=1 \
     -f "${META_SQL}"

if [[ -n "${CUTOFF_ARG}" ]]; then
    echo "Storing cutoff date (forced: ${CUTOFF_ARG})..."
    psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" \
         -v ON_ERROR_STOP=1 \
         -c "TRUNCATE public.mv_records_battus_meta; INSERT INTO public.mv_records_battus_meta (cutoff_date) VALUES ('${CUTOFF_ARG}');"
else
    echo "Storing cutoff date (auto: MAX(AAAAMMJJ) from Quotidienne)..."
    psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" \
         -v ON_ERROR_STOP=1 <<'SQL'
TRUNCATE public.mv_records_battus_meta;
INSERT INTO public.mv_records_battus_meta (cutoff_date)
SELECT MAX("AAAAMMJJ")::date FROM public."Quotidienne";
SQL
fi

echo "Cutoff date stored:"
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" \
     -c "SELECT cutoff_date FROM public.mv_records_battus_meta;"
