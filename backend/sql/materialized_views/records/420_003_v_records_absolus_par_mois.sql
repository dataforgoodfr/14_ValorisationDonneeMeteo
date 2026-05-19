CREATE OR REPLACE VIEW public.v_records_absolus_par_mois AS
WITH ranked AS (
    SELECT
        m.station_code,
        date,
        txx,
        tnn,
        ROW_NUMBER() OVER (
            PARTITION BY m.station_code, EXTRACT(MONTH FROM date)::int
            ORDER BY txx DESC NULLS LAST, date ASC
        ) AS rn_txx_max,
        ROW_NUMBER() OVER (
            PARTITION BY m.station_code, EXTRACT(MONTH FROM date)::int
            ORDER BY tnn ASC NULLS LAST, date ASC
        ) AS rn_tnn_min
    FROM public.v_mensuelle AS m
        INNER JOIN public.v_station_records AS s
            ON m.station_code = s.station_code
    WHERE txx IS NOT NULL OR tnn IS NOT NULL
)
SELECT
    station_code,
    EXTRACT(MONTH FROM date)::int AS month,
    MAX(CASE WHEN rn_txx_max = 1 THEN txx END) AS txx_max,
    MAX(CASE WHEN rn_txx_max = 1 THEN date END) AS txx_max_date,
    MAX(CASE WHEN rn_tnn_min = 1 THEN tnn END) AS tnn_min,
    MAX(CASE WHEN rn_tnn_min = 1 THEN date END) AS tnn_min_date
FROM ranked
GROUP BY station_code, EXTRACT(MONTH FROM date)::int;
