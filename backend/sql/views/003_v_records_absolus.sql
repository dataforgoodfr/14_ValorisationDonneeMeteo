-- Records progressifs par station (all-time) via window function.
--
-- Un record progressif de chaud (TX) est un jour où la station a battu
-- son propre record précédent toutes périodes confondues.
-- De même pour les records de froid (TN), direction inversée.
--
-- Note : pour des records filtrés par mois ou saison, utiliser des requêtes
-- raw SQL avec un WHERE EXTRACT(MONTH FROM "AAAAMMJJ") IN (...) avant la
-- window function (voir TimescaleTemperatureRecordsDataSource).

CREATE OR REPLACE VIEW public.v_records_absolus AS

WITH tx_ordered AS (
    SELECT
        q."NUM_POSTE",
        q."AAAAMMJJ",
        q."TX",
        MAX(q."TX") OVER (
            PARTITION BY q."NUM_POSTE"
            ORDER BY q."AAAAMMJJ"
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prev_max
    FROM public."Quotidienne" q
    WHERE q."TX" IS NOT NULL
),
tn_ordered AS (
    SELECT
        q."NUM_POSTE",
        q."AAAAMMJJ",
        q."TN",
        MIN(q."TN") OVER (
            PARTITION BY q."NUM_POSTE"
            ORDER BY q."AAAAMMJJ"
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prev_min
    FROM public."Quotidienne" q
    WHERE q."TN" IS NOT NULL
)

SELECT
    r."NUM_POSTE"  AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    'TX'::text     AS record_type,
    r."TX"         AS record_value,
    r."AAAAMMJJ"   AS record_date
FROM tx_ordered r
JOIN public.v_station s ON s.station_code = r."NUM_POSTE"
WHERE r.prev_max IS NULL OR r."TX" > r.prev_max

UNION ALL

SELECT
    r."NUM_POSTE"  AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    'TN'::text     AS record_type,
    r."TN"         AS record_value,
    r."AAAAMMJJ"   AS record_date
FROM tn_ordered r
JOIN public.v_station s ON s.station_code = r."NUM_POSTE"
WHERE r.prev_min IS NULL OR r."TN" < r.prev_min;
