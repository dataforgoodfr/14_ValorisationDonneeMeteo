-- DROP VIEW IF EXISTS public.v_records_absolus_par_saison;

CREATE OR REPLACE VIEW public.v_records_absolus_par_saison AS
WITH base AS (
    SELECT
        m.station_code,
        m.txx_max_date,
        m.tnn_min_date,
        m.txx_max,
        m.tnn_min,
        CASE
            WHEN m.month IN (12, 1, 2) THEN 1
            WHEN m.month IN (3, 4, 5) THEN 2
            WHEN m.month IN (6, 7, 8) THEN 3
            ELSE 4
        END AS season_id
    FROM public.mv_records_absolus_par_mois AS m
),
ranked AS (
    SELECT
        station_code,
        txx_max_date,
        tnn_min_date,
        txx_max,
        tnn_min,
        season_id,
        ROW_NUMBER() OVER (
            PARTITION BY station_code, season_id
            ORDER BY txx_max DESC NULLS LAST, txx_max_date ASC
        ) AS rn_txx_max,
        ROW_NUMBER() OVER (
            PARTITION BY station_code, season_id
            ORDER BY tnn_min ASC NULLS LAST, tnn_min_date ASC
        ) AS rn_tnn_min
    FROM base
)
SELECT
    station_code,
    CASE season_id
        WHEN 1 THEN 'winter'
        WHEN 2 THEN 'spring'
        WHEN 3 THEN 'summer'
        ELSE 'autumn'
    END AS season,
    MAX(CASE WHEN rn_txx_max = 1 THEN txx_max END) AS txx_max,
    MAX(CASE WHEN rn_txx_max = 1 THEN txx_max_date END) AS txx_max_date,
    MAX(CASE WHEN rn_tnn_min = 1 THEN tnn_min END) AS tnn_min,
    MAX(CASE WHEN rn_tnn_min = 1 THEN tnn_min_date END) AS tnn_min_date
FROM ranked
GROUP BY station_code, season_id;
