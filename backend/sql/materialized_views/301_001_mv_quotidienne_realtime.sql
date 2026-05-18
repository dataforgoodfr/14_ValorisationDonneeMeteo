DROP MATERIALIZED VIEW IF EXISTS public.mv_quotidienne_realtime;

CREATE MATERIALIZED VIEW public.mv_quotidienne_realtime AS
SELECT
    station_code,
    date,
    tntxm,
    tn,
    tx
FROM public.v_quotidienne_realtime;

CREATE UNIQUE INDEX IF NOT EXISTS mv_quotidienne_realtime_uq
    ON mv_quotidienne_realtime (station_code, date);
