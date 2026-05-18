CREATE OR REPLACE VIEW public.v_mensuelle AS
WITH mensuelle_climato AS (
    SELECT
        "NUM_POSTE" AS station_code,
        "AAAAMM" AS date,
        "TNAB" AS tnn,
        "TXAB" AS txx,
        "TM" AS tmm
    FROM "Mensuelle"
    WHERE "AAAAMM" < date_trunc('month', now()) - interval '2 months'
),
combined_mensuelle AS (
    SELECT station_code, date, tnn, txx, tmm FROM public.mv_mensuelle_realtime
    UNION ALL
    SELECT station_code, date, tnn, txx, tmm FROM mensuelle_climato
)
SELECT
    station_code,
    date,
    tnn,
    txx,
    tmm
FROM combined_mensuelle;
