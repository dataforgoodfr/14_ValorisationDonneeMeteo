CREATE OR REPLACE VIEW public.v_mensuelle_realtime AS
SELECT
    "station_code" AS station_code,
    date_trunc('month', "date") AS date,
    MIN("tn") AS tnn,
    MAX("tx") AS txx,
    ROUND(AVG("tntxm")::numeric, 1) AS tmm
FROM public.v_quotidienne
WHERE "date" >= date_trunc('month', now()) - interval '2 months'
GROUP BY station_code, date_trunc('month', "date");
