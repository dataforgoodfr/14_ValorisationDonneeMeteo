-- Vue matérialisée : ITN journalier sur toutes les années disponibles (>= 1946).
-- Équivalent de 610_001_mv_itn_daily_1991_2020_real.sql sans la restriction de période.
-- Accepte les jours avec au moins 29 stations sur 30 (HAVING COUNT >= 29).
-- Le filtre date >= 1946-01-01 est appliqué ici sur la colonne indexée de v_quotidienne.
CREATE OR REPLACE VIEW public.v_itn_daily_all_years AS
WITH source AS (
    SELECT
        q.station_code AS station_code,
        q.date,
        q.tntxm        AS tntxm
    FROM public.v_quotidienne q
    WHERE q.station_code IN (
        SELECT station_code FROM public.v_station_itn
    )
    AND q.date >= '1947-01-01T00:00:00+00:00'
),
normalized AS (
    SELECT *
    FROM source
    WHERE NOT (
        station_code = CASE
            WHEN date < '2012-05-08T00:00:00+00:00' THEN '51449002'
            ELSE '51183001'
        END
    )
)
SELECT
    n.date,
    EXTRACT(YEAR  FROM n.date)::int AS year,
    EXTRACT(MONTH FROM n.date)::int AS month,
    EXTRACT(DAY   FROM n.date)::int AS day_of_month,
    FALSE                           AS is_fictive,
    AVG(n.tntxm)                    AS itn
FROM normalized n
GROUP BY n.date
HAVING COUNT(DISTINCT n.station_code) >= 29;
