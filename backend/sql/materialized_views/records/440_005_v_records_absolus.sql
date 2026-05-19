-- DROP VIEW IF EXISTS public.v_records_absolus;

CREATE OR REPLACE VIEW public.v_records_absolus AS
WITH ranked AS (
    SELECT
        station_code,
        txx_max_date,
        tnn_min_date,
        txx_max,
        tnn_min,
        ROW_NUMBER() OVER (
            PARTITION BY station_code
            ORDER BY txx_max DESC NULLS LAST, txx_max_date ASC
        ) AS rn_txx_max,
        ROW_NUMBER() OVER (
            PARTITION BY station_code
            ORDER BY tnn_min ASC NULLS LAST, tnn_min_date ASC
        ) AS rn_tnn_min
    FROM public.v_records_absolus_par_saison
)
SELECT
    station_code,
    MAX(CASE WHEN rn_txx_max = 1 THEN txx_max END) AS txx_max,
    MAX(CASE WHEN rn_txx_max = 1 THEN txx_max_date END) AS txx_max_date,
    MAX(CASE WHEN rn_tnn_min = 1 THEN tnn_min END) AS tnn_min,
    MAX(CASE WHEN rn_tnn_min = 1 THEN tnn_min_date END) AS tnn_min_date
FROM ranked
GROUP BY station_code;
