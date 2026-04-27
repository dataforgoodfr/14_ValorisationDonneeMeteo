CREATE OR REPLACE VIEW public.v_quotidienne_itn AS
WITH quotidienne AS (
    SELECT
        "NUM_POSTE" AS station_code,
        "AAAAMMJJ" AS date,
        "TNTXM" AS tntxm,
        "TN" AS tn,
        "TX" AS tx
    FROM "Quotidienne"
    WHERE "AAAAMMJJ" < date_trunc('day', now()) - interval '3 days'
),

combined_quotidienne AS (
    SELECT station_code, date, tntxm, tn, tx FROM mv_quotidienne_realtime
    UNION ALL
    SELECT station_code, date, tntxm, tn, tx FROM quotidienne
)

SELECT
    station_code,
    date,
    tntxm,
    tn,
    tx
FROM combined_quotidienne
WHERE tntxm IS NOT NULL;
