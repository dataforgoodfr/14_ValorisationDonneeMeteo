CREATE OR REPLACE VIEW public.v_quotidienne_deviation AS
SELECT
    station_code,
    date,
    tntxm,
    tn,
    tx
FROM public.v_quotidienne
WHERE station_code IN (
    SELECT station_code FROM public.v_station_deviation
);
