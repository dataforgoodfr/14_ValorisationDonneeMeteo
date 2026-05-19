DROP MATERIALIZED VIEW IF EXISTS public.mv_records_absolus_par_mois;

CREATE MATERIALIZED VIEW public.mv_records_absolus_par_mois AS
SELECT
    station_code,
    month,
    txx_max,
    txx_max_date,
    tnn_min,
    tnn_min_date
FROM public.v_records_absolus_par_mois
ORDER BY station_code, month;

CREATE UNIQUE INDEX IF NOT EXISTS mv_records_absolus_par_mois_uq
    ON mv_records_absolus_par_mois (station_code, month);
