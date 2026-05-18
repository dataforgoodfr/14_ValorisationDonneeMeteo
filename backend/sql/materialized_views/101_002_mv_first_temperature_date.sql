DROP MATERIALIZED VIEW IF EXISTS public.mv_first_temperature_date;

CREATE MATERIALIZED VIEW public.mv_first_temperature_date AS
SELECT
    station_code,
    first_temperature_date
FROM public.v_first_temperature_date
ORDER BY station_code ASC;

CREATE UNIQUE INDEX IF NOT EXISTS mv_first_temperature_date_uq
    ON mv_first_temperature_date (station_code);
