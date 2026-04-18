/*
===============================================================================
VUE MATÉRIALISÉE : RECORDS PROGRESSIFS PAR STATION
===============================================================================

OBJECTIF
--------
Pré-calculer les records progressifs de température (TX max, TN min) pour
chaque station et chaque type de période (all_time, month, season).

Un record progressif est une date où la station a dépassé toutes ses valeurs
précédentes pour la même période.

STRUCTURE
---------
Colonnes :
  - period_type  : 'all_time' | 'month' | 'season'
  - period_value : NULL (all_time) | '1'–'12' (month) | 'spring'/'summer'/'autumn'/'winter'
  - record_type  : 'TX' (chaud) | 'TN' (froid)
  - station_code : identifiant station
  - station_name : nom de la station
  - department   : numéro de département
  - record_value : valeur du record (°C)
  - record_date  : date du record

UTILISATION
-----------
L'endpoint /api/v1/temperature/records lit directement cette MV via
MaterializedTemperatureRecordsDataSource. La query devient un simple SELECT
avec filtres indexés.

RAFRAÎCHISSEMENT
----------------
Commande Django : python manage.py refresh_records_mv
À exécuter après chaque import de nouvelles données quotidiennes.

PERFORMANCE
-----------
- Création : quelques minutes sur dataset complet (opération offline)
- Lecture : < 10 ms (index sur record_type, period_type, period_value)
- Volume estimé : ~170k lignes pour 1000 stations (toutes périodes confondues)
===============================================================================
*/

DROP MATERIALIZED VIEW IF EXISTS public.mv_records_battus;

CREATE MATERIALIZED VIEW public.mv_records_battus AS

WITH

-- -------------------------------------------------------------------------
-- ALL-TIME : window sur toute l'histoire de la station
-- -------------------------------------------------------------------------

tx_all AS (
    SELECT
        q."NUM_POSTE",
        q."AAAAMMJJ",
        q."TX" AS val,
        MAX(q."TX") OVER (
            PARTITION BY q."NUM_POSTE"
            ORDER BY q."AAAAMMJJ"
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prev_val
    FROM public."Quotidienne" q
    WHERE q."TX" IS NOT NULL
),

tn_all AS (
    SELECT
        q."NUM_POSTE",
        q."AAAAMMJJ",
        q."TN" AS val,
        MIN(q."TN") OVER (
            PARTITION BY q."NUM_POSTE"
            ORDER BY q."AAAAMMJJ"
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prev_val
    FROM public."Quotidienne" q
    WHERE q."TN" IS NOT NULL
),

-- -------------------------------------------------------------------------
-- MONTHLY : window partitionnée par (station, mois calendaire)
-- -------------------------------------------------------------------------

tx_monthly AS (
    SELECT
        q."NUM_POSTE",
        q."AAAAMMJJ",
        q."TX" AS val,
        EXTRACT(MONTH FROM q."AAAAMMJJ")::int AS month_num,
        MAX(q."TX") OVER (
            PARTITION BY q."NUM_POSTE", EXTRACT(MONTH FROM q."AAAAMMJJ")
            ORDER BY q."AAAAMMJJ"
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prev_val
    FROM public."Quotidienne" q
    WHERE q."TX" IS NOT NULL
),

tn_monthly AS (
    SELECT
        q."NUM_POSTE",
        q."AAAAMMJJ",
        q."TN" AS val,
        EXTRACT(MONTH FROM q."AAAAMMJJ")::int AS month_num,
        MIN(q."TN") OVER (
            PARTITION BY q."NUM_POSTE", EXTRACT(MONTH FROM q."AAAAMMJJ")
            ORDER BY q."AAAAMMJJ"
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prev_val
    FROM public."Quotidienne" q
    WHERE q."TN" IS NOT NULL
),

-- -------------------------------------------------------------------------
-- SEASONAL : window partitionnée par (station, saison)
--   winter = 12, 1, 2 | spring = 3, 4, 5
--   summer = 6, 7, 8  | autumn = 9, 10, 11
-- -------------------------------------------------------------------------

tx_seasonal AS (
    SELECT
        q."NUM_POSTE",
        q."AAAAMMJJ",
        q."TX" AS val,
        CASE EXTRACT(MONTH FROM q."AAAAMMJJ")::int
            WHEN 12 THEN 'winter' WHEN 1 THEN 'winter' WHEN 2 THEN 'winter'
            WHEN  3 THEN 'spring' WHEN 4 THEN 'spring' WHEN 5 THEN 'spring'
            WHEN  6 THEN 'summer' WHEN 7 THEN 'summer' WHEN 8 THEN 'summer'
            WHEN  9 THEN 'autumn' WHEN 10 THEN 'autumn' WHEN 11 THEN 'autumn'
        END AS season_val,
        MAX(q."TX") OVER (
            PARTITION BY q."NUM_POSTE",
                CASE EXTRACT(MONTH FROM q."AAAAMMJJ")::int
                    WHEN 12 THEN 'winter' WHEN 1 THEN 'winter' WHEN 2 THEN 'winter'
                    WHEN  3 THEN 'spring' WHEN 4 THEN 'spring' WHEN 5 THEN 'spring'
                    WHEN  6 THEN 'summer' WHEN 7 THEN 'summer' WHEN 8 THEN 'summer'
                    WHEN  9 THEN 'autumn' WHEN 10 THEN 'autumn' WHEN 11 THEN 'autumn'
                END
            ORDER BY q."AAAAMMJJ"
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prev_val
    FROM public."Quotidienne" q
    WHERE q."TX" IS NOT NULL
),

tn_seasonal AS (
    SELECT
        q."NUM_POSTE",
        q."AAAAMMJJ",
        q."TN" AS val,
        CASE EXTRACT(MONTH FROM q."AAAAMMJJ")::int
            WHEN 12 THEN 'winter' WHEN 1 THEN 'winter' WHEN 2 THEN 'winter'
            WHEN  3 THEN 'spring' WHEN 4 THEN 'spring' WHEN 5 THEN 'spring'
            WHEN  6 THEN 'summer' WHEN 7 THEN 'summer' WHEN 8 THEN 'summer'
            WHEN  9 THEN 'autumn' WHEN 10 THEN 'autumn' WHEN 11 THEN 'autumn'
        END AS season_val,
        MIN(q."TN") OVER (
            PARTITION BY q."NUM_POSTE",
                CASE EXTRACT(MONTH FROM q."AAAAMMJJ")::int
                    WHEN 12 THEN 'winter' WHEN 1 THEN 'winter' WHEN 2 THEN 'winter'
                    WHEN  3 THEN 'spring' WHEN 4 THEN 'spring' WHEN 5 THEN 'spring'
                    WHEN  6 THEN 'summer' WHEN 7 THEN 'summer' WHEN 8 THEN 'summer'
                    WHEN  9 THEN 'autumn' WHEN 10 THEN 'autumn' WHEN 11 THEN 'autumn'
                END
            ORDER BY q."AAAAMMJJ"
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prev_val
    FROM public."Quotidienne" q
    WHERE q."TN" IS NOT NULL
)

-- All-time chaud
SELECT
    'all_time'   AS period_type,
    NULL::text   AS period_value,
    'TX'         AS record_type,
    r."NUM_POSTE"    AS station_code,
    s.name           AS station_name,
    s.departement    AS department,
    r.val            AS record_value,
    r."AAAAMMJJ"     AS record_date
FROM tx_all r
JOIN public.v_station s ON s.station_code = r."NUM_POSTE"
WHERE (r.prev_val IS NULL OR r.val > r.prev_val)
  AND r."AAAAMMJJ" >= make_date(s.annee_de_creation + 20, 1, 1)

UNION ALL

-- All-time froid
SELECT
    'all_time'       AS period_type,
    NULL::text       AS period_value,
    'TN'             AS record_type,
    r."NUM_POSTE"    AS station_code,
    s.name           AS station_name,
    s.departement    AS department,
    r.val            AS record_value,
    r."AAAAMMJJ"     AS record_date
FROM tn_all r
JOIN public.v_station s ON s.station_code = r."NUM_POSTE"
WHERE (r.prev_val IS NULL OR r.val < r.prev_val)
  AND r."AAAAMMJJ" >= make_date(s.annee_de_creation + 20, 1, 1)

UNION ALL

-- Monthly chaud
SELECT
    'month'              AS period_type,
    r.month_num::text    AS period_value,
    'TX'                 AS record_type,
    r."NUM_POSTE"        AS station_code,
    s.name               AS station_name,
    s.departement        AS department,
    r.val                AS record_value,
    r."AAAAMMJJ"         AS record_date
FROM tx_monthly r
JOIN public.v_station s ON s.station_code = r."NUM_POSTE"
WHERE (r.prev_val IS NULL OR r.val > r.prev_val)
  AND r."AAAAMMJJ" >= make_date(s.annee_de_creation + 20, 1, 1)

UNION ALL

-- Monthly froid
SELECT
    'month'              AS period_type,
    r.month_num::text    AS period_value,
    'TN'                 AS record_type,
    r."NUM_POSTE"        AS station_code,
    s.name               AS station_name,
    s.departement        AS department,
    r.val                AS record_value,
    r."AAAAMMJJ"         AS record_date
FROM tn_monthly r
JOIN public.v_station s ON s.station_code = r."NUM_POSTE"
WHERE (r.prev_val IS NULL OR r.val < r.prev_val)
  AND r."AAAAMMJJ" >= make_date(s.annee_de_creation + 20, 1, 1)

UNION ALL

-- Seasonal chaud
SELECT
    'season'         AS period_type,
    r.season_val     AS period_value,
    'TX'             AS record_type,
    r."NUM_POSTE"    AS station_code,
    s.name           AS station_name,
    s.departement    AS department,
    r.val            AS record_value,
    r."AAAAMMJJ"     AS record_date
FROM tx_seasonal r
JOIN public.v_station s ON s.station_code = r."NUM_POSTE"
WHERE (r.prev_val IS NULL OR r.val > r.prev_val)
  AND r."AAAAMMJJ" >= make_date(s.annee_de_creation + 20, 1, 1)

UNION ALL

-- Seasonal froid
SELECT
    'season'         AS period_type,
    r.season_val     AS period_value,
    'TN'             AS record_type,
    r."NUM_POSTE"    AS station_code,
    s.name           AS station_name,
    s.departement    AS department,
    r.val            AS record_value,
    r."AAAAMMJJ"     AS record_date
FROM tn_seasonal r
JOIN public.v_station s ON s.station_code = r."NUM_POSTE"
WHERE (r.prev_val IS NULL OR r.val < r.prev_val)
  AND r."AAAAMMJJ" >= make_date(s.annee_de_creation + 20, 1, 1);

-- ============================================================================
-- INDEX
-- ============================================================================

-- Index principal utilisé par l'endpoint (filtre sur les 3 colonnes de recherche)
CREATE INDEX idx_mv_records_battus_query
ON public.mv_records_battus (record_type, period_type, period_value);

-- Index secondaire pour les requêtes par station (diagnostic, admin)
CREATE INDEX idx_mv_records_battus_station
ON public.mv_records_battus (station_code);
