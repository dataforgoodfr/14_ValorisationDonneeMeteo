CREATE OR REPLACE VIEW public.v_quotidienne_itn AS
WITH horaire_from_infrahoraire AS (
    SELECT
        geo_id_insee                                                                AS station_id,
        date_trunc('hour', validity_time - interval '1 second') + interval '1 hour' AS timestamp,
        LAST(t, validity_time)                                                      AS t,
        MIN(t)                                                                      AS tn,
        MAX(t)                                                                      AS tx
    FROM "InfrahoraireTempsReel"
    WHERE validity_time > date_trunc('hour', now()) - interval '3 hours'
    GROUP BY station_id, date_trunc('hour', validity_time - interval '1 second') + interval '1 hour'
),

horaire_temps_reel AS (
    SELECT
        geo_id_insee AS station_id,
        validity_time AS timestamp,
        t AS t,
        tn AS tn,
        tx AS tx
    FROM "HoraireTempsReel"
    WHERE date_trunc('hour', now()) - interval '36 hours' <= validity_time AND validity_time <= date_trunc('hour', now()) - interval '3 hours'
),

horaire AS (
    SELECT
        "NUM_POSTE" AS station_id,
        "AAAAMMJJHH" AS timestamp,
        "T" AS t,
        "TN" AS tn,
        "TX" AS tx
    FROM "Horaire"
    WHERE date_trunc('day', now()) - interval '4 days' <= "AAAAMMJJHH" AND "AAAAMMJJHH" < date_trunc('hour', now()) - interval '36 hours'
),

combined_horaire AS (
    SELECT station_id, timestamp, t, tn, tx FROM horaire_from_infrahoraire
    UNION ALL
    SELECT station_id, timestamp, t, tn, tx FROM horaire_temps_reel
    UNION ALL
    SELECT station_id, timestamp, t, tn, tx FROM horaire
),

tn_quotidienne_temps_reel AS (
    SELECT
        station_id                                                                                  AS station_id,
        date_trunc('day', timestamp - interval '18 hours' - interval '1 second') + interval '1 day' AS timestamp,
        MIN(tn)                                                                                     AS tn
    FROM combined_horaire
    WHERE timestamp > date_trunc('day', now()) - interval '4 days' + interval '18 hours'
    GROUP BY station_id, date_trunc('day', timestamp - interval '18 hours' - interval '1 second') + interval '1 day'
),

tx_quotidienne_temps_reel AS (
    SELECT
        station_id                                                              AS station_id,
        date_trunc('day', timestamp - interval '6 hours' - interval '1 second') AS timestamp,
        MAX(tx)                                                                 AS tx
    FROM combined_horaire
    WHERE timestamp > date_trunc('day', now()) - interval '3 days' + interval '6 hours'
    GROUP BY station_id, date_trunc('day', timestamp - interval '6 hours' - interval '1 second')
),

tn_tx_quotidienne_temps_reel AS (
    SELECT station_id, timestamp, tn, NULL::numeric AS tx FROM tn_quotidienne_temps_reel
    UNION ALL
    SELECT station_id, timestamp, NULL::numeric AS tn, tx FROM tx_quotidienne_temps_reel
),

quotidienne_temps_reel AS (
    SELECT
        station_id,
        timestamp,
        (MIN(tn) + MAX(tx)) / 2.0 AS tntxm,
        MIN(tn)                   AS tn,
        MAX(tx)                   AS tx
    FROM tn_tx_quotidienne_temps_reel
    WHERE timestamp >= date_trunc('day', now()) - interval '3 days'
    GROUP BY station_id, timestamp
),

quotidienne AS (
    SELECT
        "NUM_POSTE" AS station_id,
        "AAAAMMJJ" AS timestamp,
        "TNTXM" AS tntxm,
        "TN" AS tn,
        "TX" AS tx
    FROM "Quotidienne"
    WHERE "AAAAMMJJ" < date_trunc('day', now()) - interval '3 days'
),

combined_quotidienne AS (
    SELECT station_id, timestamp, tntxm, tn, tx FROM quotidienne_temps_reel
    UNION ALL
    SELECT station_id, timestamp, tntxm, tn, tx FROM quotidienne
)

SELECT
    station_id AS station_code,
    timestamp::timestamp(3) AS date,
    tntxm AS tntxm,
    tn AS tn,
    tx AS tx
FROM combined_quotidienne
WHERE tntxm IS NOT NULL;
