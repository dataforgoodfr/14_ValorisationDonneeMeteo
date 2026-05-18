DROP MATERIALIZED VIEW IF EXISTS public.mv_mensuelle_realtime;

CREATE MATERIALIZED VIEW public.mv_mensuelle_realtime AS
SELECT
    "station_code" AS station_code,
    date_trunc('month', "date") AS date,
    MIN("tn") AS tnn,
    MAX("tx") AS txx,
    ROUND(AVG("tntxm")::numeric, 1) AS tmm
FROM "v_quotidienne"
WHERE "date" >= date_trunc('month', now()) - interval '2 months'
GROUP BY station_code, date_trunc('month', "date")
ORDER BY station_code, date;

CREATE UNIQUE INDEX IF NOT EXISTS mv_mensuelle_realtime_uq
    ON mv_mensuelle_realtime (station_code, date);
