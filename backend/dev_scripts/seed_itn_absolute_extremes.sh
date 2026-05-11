#!/usr/bin/env bash
# Seed les tables des extremes absolus de l'ITN en environnement de développement.
# En prod, ces objets sont des vues matérialisées (006-010_mv_itn_absolute_extremes_*.sql).
# En dev, on les crée comme des tables ordinaires et on les alimente en calculant
# directement depuis v_quotidienne_itn (les données doivent déjà être chargées).
#
# Usage :
#   ./seed_itn_absolute_extremes.sh

set -euo pipefail

: "${DB_HOST:?DB_HOST is required}"
: "${DB_PORT:?DB_PORT is required}"
: "${DB_NAME:?DB_NAME is required}"
: "${DB_USER:?DB_USER is required}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"

export PGPASSWORD="$DB_PASSWORD"

_drop_mv_or_table() {
  local TABLE_NAME="$1"
  psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relname = '${TABLE_NAME}' AND c.relkind = 'm'
    ) THEN
        EXECUTE 'DROP MATERIALIZED VIEW public.${TABLE_NAME}';
    ELSIF EXISTS (
        SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relname = '${TABLE_NAME}' AND c.relkind = 'r'
    ) THEN
        EXECUTE 'DROP TABLE public.${TABLE_NAME}';
    END IF;
END
\$\$;
SQL
}

# ── Common CTE (inlines 006 + 007 logic) ───────────────────────────────────
# Reproduit mv_itn_daily_all_years (006) puis mv_itn_daily_all_years_with_feb29 (007).
ITN_DAILY_CTE="
WITH source AS (
    SELECT q.station_code, q.date, q.tntxm
    FROM v_quotidienne_itn q
    WHERE q.station_code IN (
        '47091001','20148001','25056001','33281001','73054001',
        '29075001','14137001','36063001','63113001','16089001',
        '21473001','72181001','59343001','69029001','13054001',
        '26198001','54526001','44020001','58160001','06088001',
        '30189001','45055001','75114001','64549001','66136001',
        '86027001','35281001','67124001','31069001',
        '51183001','51449002'
    )
),
normalized AS (
    SELECT *
    FROM source
    WHERE NOT (
        station_code = CASE
            WHEN date < DATE '2012-05-08' THEN '51449002'
            ELSE '51183001'
        END
    )
),
daily_itn AS (
    SELECT
        n.date,
        EXTRACT(YEAR  FROM n.date)::int AS year,
        EXTRACT(MONTH FROM n.date)::int AS month,
        EXTRACT(DAY   FROM n.date)::int AS day_of_month,
        FALSE                           AS is_fictive,
        AVG(n.tntxm)                    AS itn
    FROM normalized n
    GROUP BY n.date
    HAVING COUNT(DISTINCT n.station_code) >= 29
),
feb29_fictive AS (
    SELECT
        NULL::date AS date,
        feb28.year,
        2          AS month,
        29         AS day_of_month,
        TRUE       AS is_fictive,
        (feb28.itn + mar01.itn) / 2.0 AS itn
    FROM daily_itn feb28
    INNER JOIN daily_itn mar01
        ON  mar01.year         = feb28.year
        AND mar01.month        = 3
        AND mar01.day_of_month = 1
    WHERE feb28.month        = 2
      AND feb28.day_of_month = 28
      AND NOT (
          (feb28.year % 4 = 0 AND feb28.year % 100 <> 0)
          OR (feb28.year % 400 = 0)
      )
),
all_days AS (
    SELECT * FROM daily_itn
    UNION ALL
    SELECT * FROM feb29_fictive
)"

# ── Daily ──────────────────────────────────────────────────────────────────
echo "Seeding mv_itn_absolute_extremes_daily from v_quotidienne_itn"
_drop_mv_or_table "mv_itn_absolute_extremes_daily"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 <<SQL
CREATE TABLE public.mv_itn_absolute_extremes_daily (
    month        integer          NOT NULL,
    day_of_month integer          NOT NULL,
    absolute_min double precision NOT NULL,
    absolute_max double precision NOT NULL,
    CONSTRAINT pk_mv_itn_absolute_extremes_daily PRIMARY KEY (month, day_of_month)
);
INSERT INTO public.mv_itn_absolute_extremes_daily (month, day_of_month, absolute_min, absolute_max)
${ITN_DAILY_CTE}
SELECT month, day_of_month, MIN(itn) AS absolute_min, MAX(itn) AS absolute_max
FROM all_days
WHERE year >= 1946
GROUP BY month, day_of_month
ORDER BY month, day_of_month;
SQL

# ── Monthly ────────────────────────────────────────────────────────────────
echo "Seeding mv_itn_absolute_extremes_monthly from v_quotidienne_itn"
_drop_mv_or_table "mv_itn_absolute_extremes_monthly"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 <<SQL
CREATE TABLE public.mv_itn_absolute_extremes_monthly (
    month        integer          NOT NULL,
    absolute_min double precision NOT NULL,
    absolute_max double precision NOT NULL,
    CONSTRAINT pk_mv_itn_absolute_extremes_monthly PRIMARY KEY (month)
);
INSERT INTO public.mv_itn_absolute_extremes_monthly (month, absolute_min, absolute_max)
${ITN_DAILY_CTE},
monthly_itn AS (
    SELECT year, month, AVG(itn) AS monthly_mean
    FROM all_days
    WHERE NOT is_fictive AND year >= 1946
    GROUP BY year, month
)
SELECT month, MIN(monthly_mean) AS absolute_min, MAX(monthly_mean) AS absolute_max
FROM monthly_itn
GROUP BY month
ORDER BY month;
SQL

# ── Yearly ─────────────────────────────────────────────────────────────────
echo "Seeding mv_itn_absolute_extremes_yearly from v_quotidienne_itn"
_drop_mv_or_table "mv_itn_absolute_extremes_yearly"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 <<SQL
CREATE TABLE public.mv_itn_absolute_extremes_yearly (
    absolute_min double precision NOT NULL,
    absolute_max double precision NOT NULL
);
INSERT INTO public.mv_itn_absolute_extremes_yearly (absolute_min, absolute_max)
${ITN_DAILY_CTE},
yearly_itn AS (
    SELECT year, AVG(itn) AS yearly_mean
    FROM all_days
    WHERE NOT is_fictive AND year >= 1946
    GROUP BY year
)
SELECT MIN(yearly_mean) AS absolute_min, MAX(yearly_mean) AS absolute_max
FROM yearly_itn;
SQL

echo "Done seeding itn absolute extremes."
