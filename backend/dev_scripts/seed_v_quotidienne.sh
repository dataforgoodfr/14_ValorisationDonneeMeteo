#!/usr/bin/env bash
set -euo pipefail

: "${DB_HOST:?DB_HOST is required}"
: "${DB_PORT:?DB_PORT is required}"
: "${DB_NAME:?DB_NAME is required}"
: "${DB_USER:?DB_USER is required}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"

export PGPASSWORD="$DB_PASSWORD"

psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 <<'SQL'
DROP VIEW IF EXISTS public.v_quotidienne_itn CASCADE;
DROP VIEW IF EXISTS public.v_quotidienne CASCADE;

CREATE VIEW public.v_quotidienne AS
SELECT
    q."NUM_POSTE" AS station_code,
    q."AAAAMMJJ"::date AS date,
    q."TN" AS tn,
    q."TX" AS tx,
    q."TNTXM" AS tntxm
FROM public."Quotidienne" q;

CREATE VIEW public.v_quotidienne_itn AS
SELECT
    station_code,
    date,
    tntxm
FROM public.v_quotidienne
WHERE tntxm IS NOT NULL;
SQL
