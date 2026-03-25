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

if [[ ! -d "$VIEWS_DIR" ]]; then
  echo "ERROR: views directory not found: $VIEWS_DIR" >&2
  exit 1
fi

for f in "$VIEWS_DIR"/*.sql; do
  echo "Applying $(basename "$f")"
  psql -h "$DB_HOST" \
       -p "$DB_PORT" \
       -U "$DB_USER" \
       -d "$DB_NAME" \
       -v ON_ERROR_STOP=1 \
       -f "$f"
done

echo "Sanity checks:"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<'SQL'
SELECT COUNT(*) AS v_station_count FROM public.v_station;
SELECT COUNT(*) AS v_quotidienne_itn_count FROM public.v_quotidienne_itn;
SQL

echo "Views applied."
