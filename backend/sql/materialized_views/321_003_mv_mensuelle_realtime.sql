DROP MATERIALIZED VIEW IF EXISTS public.mv_mensuelle_realtime;

CREATE MATERIALIZED VIEW public.mv_mensuelle_realtime AS
SELECT
    station_code,
    date,
    tnn,
    txx,
    tmm
FROM public.v_mensuelle_realtime
ORDER BY station_code, date;

CREATE UNIQUE INDEX IF NOT EXISTS mv_mensuelle_realtime_uq
    ON mv_mensuelle_realtime (station_code, date);
