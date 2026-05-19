DROP MATERIALIZED VIEW IF EXISTS public.mv_itn_daily_all_years CASCADE;

DROP MATERIALIZED VIEW IF EXISTS public.mv_itn_daily_1991_2020_real CASCADE;

DROP MATERIALIZED VIEW IF EXISTS public.mv_baseline_station_daily_mean_1991_2020;

DROP MATERIALIZED VIEW IF EXISTS public.mv_records_absolus_par_mois CASCADE;

DROP MATERIALIZED VIEW IF EXISTS public.mv_records_battus;

DROP MATERIALIZED VIEW IF EXISTS public.mv_mensuelle_realtime CASCADE;

DROP MATERIALIZED VIEW IF EXISTS public.mv_quotidienne_realtime CASCADE;

DROP MATERIALIZED VIEW IF EXISTS public.mv_first_temperature_date CASCADE;

CREATE OR REPLACE VIEW public.v_first_temperature_date AS
SELECT
    "NUM_POSTE"   AS station_code,
    MIN("AAAAMM") AS first_temperature_date
FROM public."Mensuelle"
WHERE "TM" IS NOT NULL
GROUP BY "NUM_POSTE";

CREATE MATERIALIZED VIEW public.mv_first_temperature_date AS
SELECT
    station_code,
    first_temperature_date
FROM public.v_first_temperature_date
ORDER BY station_code ASC;

CREATE UNIQUE INDEX IF NOT EXISTS mv_first_temperature_date_uq
    ON public.mv_first_temperature_date (station_code);

CREATE OR REPLACE VIEW public.v_station_qualifiee_hexagone AS
WITH station_classe_recente AS (
    SELECT station_code, classe
    FROM public."station_classe"
    WHERE date_fin IS NULL
)
SELECT DISTINCT ON (s."id")
    s."id" AS station_code,
    s."nom" AS name,
    s."departement" AS departement,
    s."posteOuvert" AS is_open,
    s."typePoste" AS station_type,
    s."lon" AS lon,
    s."lat" AS lat,
    s."alt" AS alt,
    s."postePublic" AS is_public,
    scr."classe" AS classe_recente,
    scd."date_de_creation" AS date_de_creation,
    scd."date_de_fermeture" AS date_de_fermeture,
    EXTRACT (YEAR FROM scd."date_de_creation")::int AS annee_de_creation,
    EXTRACT (YEAR FROM scd."date_de_fermeture")::int AS annee_de_fermeture,
    ftd."first_temperature_date" AS first_temperature_date
FROM public."Station" s
    JOIN public."station_creation_date" scd
        ON s."id" = scd."station_code"
    LEFT JOIN station_classe_recente scr
        ON s."id" = scr."station_code"
    JOIN public."mv_first_temperature_date" ftd
        ON s."id" = ftd."station_code"
WHERE s."typePoste" <= 3
    AND s.departement < '96';

CREATE OR REPLACE VIEW public.v_station_classe_1234 AS
SELECT
    s.station_code,
    s.name,
    s.departement,
    s.is_open,
    s.station_type,
    s.lon,
    s.lat,
    s.alt,
    s.is_public,
    s.classe_recente,
    s.date_de_creation,
    s.date_de_fermeture,
    s.annee_de_creation,
    s.annee_de_fermeture,
    s.first_temperature_date
FROM public.v_station_qualifiee_hexagone s
WHERE s.classe_recente <= 4;

CREATE OR REPLACE VIEW public.v_station_classe_123 AS
SELECT
    s.station_code,
    s.name,
    s.departement,
    s.is_open,
    s.station_type,
    s.lon,
    s.lat,
    s.alt,
    s.is_public,
    s.classe_recente,
    s.date_de_creation,
    s.date_de_fermeture,
    s.annee_de_creation,
    s.annee_de_fermeture,
    s.first_temperature_date
FROM public.v_station_classe_1234 s
WHERE s.classe_recente <= 3;

CREATE OR REPLACE VIEW public.v_quotidienne_realtime AS
WITH horaire_from_infrahoraire AS (
    SELECT
        geo_id_insee                                                                AS station_id,
        date_trunc('hour', validity_time - interval '1 second') + interval '1 hour' AS timestamp,
        LAST(t, validity_time)                                                      AS t,
        MIN(t)                                                                      AS tn,
        MAX(t)                                                                      AS tx
    FROM public."InfrahoraireTempsReel"
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
    FROM public."HoraireTempsReel"
    WHERE date_trunc('hour', now()) - interval '36 hours' <= validity_time AND validity_time <= date_trunc('hour', now()) - interval '3 hours'
),

horaire AS (
    SELECT
        "NUM_POSTE" AS station_id,
        "AAAAMMJJHH" AS timestamp,
        "T" AS t,
        "TN" AS tn,
        "TX" AS tx
    FROM public."Horaire"
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
)

SELECT
    station_id AS station_code,
    timestamp::timestamp(3) AS date,
    tntxm AS tntxm,
    tn AS tn,
    tx AS tx
FROM quotidienne_temps_reel
WHERE tntxm IS NOT NULL;

CREATE MATERIALIZED VIEW public.mv_quotidienne_realtime AS
SELECT
    station_code,
    date,
    tntxm,
    tn,
    tx
FROM public.v_quotidienne_realtime;

CREATE UNIQUE INDEX IF NOT EXISTS mv_quotidienne_realtime_uq
    ON public.mv_quotidienne_realtime (station_code, date);

CREATE OR REPLACE VIEW public.v_quotidienne AS
WITH quotidienne AS (
    SELECT
        "NUM_POSTE" AS station_code,
        "AAAAMMJJ" AS date,
        "TNTXM" AS tntxm,
        "TN" AS tn,
        "TX" AS tx
    FROM public."Quotidienne"
    WHERE "AAAAMMJJ" < date_trunc('day', now()) - interval '3 days'
),

combined_quotidienne AS (
    SELECT station_code, date, tntxm, tn, tx FROM public.mv_quotidienne_realtime
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
    ON public.mv_mensuelle_realtime (station_code, date);

CREATE OR REPLACE VIEW public.v_mensuelle AS
WITH mensuelle_climato AS (
    SELECT
        "NUM_POSTE" AS station_code,
        "AAAAMM" AS date,
        "TNAB" AS tnn,
        "TXAB" AS txx,
        "TM" AS tmm
    FROM public."Mensuelle"
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

CREATE OR REPLACE VIEW public.v_station_records AS
SELECT
    s.station_code,
    s.name,
    s.departement,
    s.is_open,
    s.station_type,
    s.lon,
    s.lat,
    s.alt,
    s.is_public,
    s.classe_recente,
    s.date_de_creation,
    s.date_de_fermeture,
    s.annee_de_creation,
    s.annee_de_fermeture,
    s.first_temperature_date
FROM public.v_station_classe_123 s
WHERE s.first_temperature_date <= now() - interval '50 year';

CREATE OR REPLACE VIEW public.v_records_absolus_par_mois AS
WITH ranked AS (
    SELECT
        m.station_code,
        date,
        txx,
        tnn,
        ROW_NUMBER() OVER (
            PARTITION BY m.station_code, EXTRACT(MONTH FROM date)::int
            ORDER BY txx DESC NULLS LAST, date ASC
        ) AS rn_txx_max,
        ROW_NUMBER() OVER (
            PARTITION BY m.station_code, EXTRACT(MONTH FROM date)::int
            ORDER BY tnn ASC NULLS LAST, date ASC
        ) AS rn_tnn_min
    FROM public.v_mensuelle AS m
        INNER JOIN public.v_station_records AS s
            ON m.station_code = s.station_code
    WHERE txx IS NOT NULL OR tnn IS NOT NULL
)
SELECT
    station_code,
    EXTRACT(MONTH FROM date)::int AS month,
    MAX(CASE WHEN rn_txx_max = 1 THEN txx END) AS txx_max,
    MAX(CASE WHEN rn_txx_max = 1 THEN date END) AS txx_max_date,
    MAX(CASE WHEN rn_tnn_min = 1 THEN tnn END) AS tnn_min,
    MAX(CASE WHEN rn_tnn_min = 1 THEN date END) AS tnn_min_date
FROM ranked
GROUP BY station_code, EXTRACT(MONTH FROM date)::int;

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
    ON public.mv_records_absolus_par_mois (station_code, month);

CREATE OR REPLACE VIEW public.v_records_absolus_par_saison AS
WITH base AS (
    SELECT
        m.station_code,
        m.txx_max_date,
        m.tnn_min_date,
        m.txx_max,
        m.tnn_min,
        CASE
            WHEN m.month IN (12, 1, 2) THEN 1
            WHEN m.month IN (3, 4, 5) THEN 2
            WHEN m.month IN (6, 7, 8) THEN 3
            ELSE 4
        END AS season_id
    FROM public.mv_records_absolus_par_mois AS m
),
ranked AS (
    SELECT
        station_code,
        txx_max_date,
        tnn_min_date,
        txx_max,
        tnn_min,
        season_id,
        ROW_NUMBER() OVER (
            PARTITION BY station_code, season_id
            ORDER BY txx_max DESC NULLS LAST, txx_max_date ASC
        ) AS rn_txx_max,
        ROW_NUMBER() OVER (
            PARTITION BY station_code, season_id
            ORDER BY tnn_min ASC NULLS LAST, tnn_min_date ASC
        ) AS rn_tnn_min
    FROM base
)
SELECT
    station_code,
    CASE season_id
        WHEN 1 THEN 'winter'
        WHEN 2 THEN 'spring'
        WHEN 3 THEN 'summer'
        ELSE 'autumn'
    END AS season,
    MAX(CASE WHEN rn_txx_max = 1 THEN txx_max END) AS txx_max,
    MAX(CASE WHEN rn_txx_max = 1 THEN txx_max_date END) AS txx_max_date,
    MAX(CASE WHEN rn_tnn_min = 1 THEN tnn_min END) AS tnn_min,
    MAX(CASE WHEN rn_tnn_min = 1 THEN tnn_min_date END) AS tnn_min_date
FROM ranked
GROUP BY station_code, season_id;

CREATE OR REPLACE VIEW public.v_records_absolus AS
WITH ranked AS (
    SELECT
        station_code,
        txx_max_date,
        tnn_min_date,
        txx_max,
        tnn_min,
        ROW_NUMBER() OVER (
            PARTITION BY station_code
            ORDER BY txx_max DESC NULLS LAST, txx_max_date ASC
        ) AS rn_txx_max,
        ROW_NUMBER() OVER (
            PARTITION BY station_code
            ORDER BY tnn_min ASC NULLS LAST, tnn_min_date ASC
        ) AS rn_tnn_min
    FROM public.v_records_absolus_par_saison
)
SELECT
    station_code,
    MAX(CASE WHEN rn_txx_max = 1 THEN txx_max END) AS txx_max,
    MAX(CASE WHEN rn_txx_max = 1 THEN txx_max_date END) AS txx_max_date,
    MAX(CASE WHEN rn_tnn_min = 1 THEN tnn_min END) AS tnn_min,
    MAX(CASE WHEN rn_tnn_min = 1 THEN tnn_min_date END) AS tnn_min_date
FROM ranked
GROUP BY station_code;

CREATE OR REPLACE VIEW public.v_records_absolus_par_type AS

-- All-time chaud
SELECT
    'all_time'     AS period_type,
    NULL::text     AS period_value,
    'TX'           AS record_type,
    m.station_code AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    m.txx_max      AS record_value,
    m.txx_max_date AS record_date
FROM public.v_records_absolus m
    JOIN public.v_station_records s
        ON s.station_code = m.station_code

UNION ALL

-- All-time froid
SELECT
    'all_time'     AS period_type,
    NULL::text     AS period_value,
    'TN'           AS record_type,
    m.station_code AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    m.tnn_min      AS record_value,
    m.tnn_min_date AS record_date
FROM public.v_records_absolus m
    JOIN public.v_station_records s
        ON s.station_code = m.station_code

UNION ALL

-- Seasonal chaud
SELECT
    'season'       AS period_type,
    m.season::text AS period_value,
    'TX'           AS record_type,
    m.station_code AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    m.txx_max      AS record_value,
    m.txx_max_date AS record_date
FROM public.v_records_absolus_par_saison m
    JOIN public.v_station_records s
        ON s.station_code = m.station_code

UNION ALL

-- Seasonal froid
SELECT
    'season'       AS period_type,
    m.season::text AS period_value,
    'TN'           AS record_type,
    m.station_code AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    m.tnn_min      AS record_value,
    m.tnn_min_date AS record_date
FROM public.v_records_absolus_par_saison m
    JOIN public.v_station_records s
        ON s.station_code = m.station_code

UNION ALL

-- Monthly chaud
SELECT
    'month'        AS period_type,
    m.month::text  AS period_value,
    'TX'           AS record_type,
    m.station_code AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    m.txx_max      AS record_value,
    m.txx_max_date AS record_date
FROM public.mv_records_absolus_par_mois m
    JOIN public.v_station_records s
        ON s.station_code = m.station_code

UNION ALL

-- Monthly froid
SELECT
    'month'        AS period_type,
    m.month::text  AS period_value,
    'TN'           AS record_type,
    m.station_code AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    m.tnn_min      AS record_value,
    m.tnn_min_date AS record_date
FROM public.mv_records_absolus_par_mois m
    JOIN public.v_station_records s
        ON s.station_code = m.station_code;

CREATE OR REPLACE VIEW public.v_station_deviation AS
SELECT
    s.station_code,
    s.name,
    s.departement,
    s.is_open,
    s.station_type,
    s.lon,
    s.lat,
    s.alt,
    s.is_public,
    s.classe_recente,
    s.date_de_creation,
    s.date_de_fermeture,
    s.annee_de_creation,
    s.annee_de_fermeture,
    s.first_temperature_date
FROM public.v_station_classe_1234 s
WHERE s.first_temperature_date < '1997-01-01T00:00:00+00:00';

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

CREATE OR REPLACE VIEW public.v_baseline_station_daily_mean_1991_2020 AS

WITH quotidienne_1991_2020 AS (
    SELECT
        "NUM_POSTE" AS station_code,
        "AAAAMMJJ" AS date,
        "TNTXM" AS tntxm
    FROM public."Quotidienne"
    WHERE '1991-01-01T00:00:00+00:00' <= "AAAAMMJJ" AND "AAAAMMJJ" < '2021-01-01T00:00:00+00:00'
        AND "TNTXM" IS NOT NULL
        AND "NUM_POSTE" IN (
            SELECT station_code FROM public.v_station_deviation
        )
),

base AS (
    SELECT
        v.station_code,
        v.date,
        v.tntxm,
        EXTRACT(YEAR  FROM v.date)::int AS year,
        EXTRACT(MONTH FROM v.date)::int AS month,
        EXTRACT(DAY   FROM v.date)::int AS day
    FROM quotidienne_1991_2020 v
),

normal_days AS (
    SELECT
        b.station_code,
        b.year,
        b.month,
        b.day,
        b.tntxm AS daily_value
    FROM base b
    WHERE NOT (b.month = 2 AND b.day = 29)
),

leap_feb29 AS (
    SELECT
        b.station_code,
        b.year,
        2 AS month,
        29 AS day,
        b.tntxm AS daily_value
    FROM base b
    WHERE b.month = 2
      AND b.day = 29
),

non_leap_feb29 AS (
    SELECT
        x.station_code,
        x.year,
        2 AS month,
        29 AS day,
        CASE
            WHEN COUNT(*) = 2 THEN AVG(x.tntxm)
            ELSE NULL
        END AS daily_value
    FROM (
        SELECT station_code, year, tntxm
        FROM base
        WHERE month = 2 AND day = 28

        UNION ALL

        SELECT station_code, year, tntxm
        FROM base
        WHERE month = 3 AND day = 1
    ) x
    WHERE NOT (
        (x.year % 4 = 0 AND x.year % 100 <> 0)
        OR x.year % 400 = 0
    )
    GROUP BY x.station_code, x.year
),

normalized_daily AS (
    SELECT * FROM normal_days
    UNION ALL
    SELECT * FROM leap_feb29
    UNION ALL
    SELECT * FROM non_leap_feb29
    WHERE daily_value IS NOT NULL
)

SELECT
    nd.station_code,
    nd.month,
    nd.day,
    COUNT(nd.daily_value) AS sample_count,
    ROUND(AVG(nd.daily_value)::numeric, 2) AS baseline_mean_tntxm
FROM normalized_daily nd
GROUP BY
    nd.station_code,
    nd.month,
    nd.day
HAVING COUNT(nd.daily_value) >= 24;

CREATE MATERIALIZED VIEW public.mv_baseline_station_daily_mean_1991_2020 AS
SELECT
    station_code,
    month,
    day,
    sample_count,
    baseline_mean_tntxm
FROM public.v_baseline_station_daily_mean_1991_2020;

CREATE INDEX IF NOT EXISTS idx_mv_baseline_station_daily_mean
ON public.mv_baseline_station_daily_mean_1991_2020 (station_code, month, day);

CREATE OR REPLACE VIEW public.v_station_itn AS
SELECT
    s.station_code,
    s.name,
    s.departement,
    s.is_open,
    s.station_type,
    s.lon,
    s.lat,
    s.alt,
    s.is_public,
    s.classe_recente,
    s.date_de_creation,
    s.date_de_fermeture,
    s.first_temperature_date
FROM public.v_station_qualifiee_hexagone s
WHERE s.station_code IN (
    '06088001',
    '13054001',
    '14137001',
    '16089001',
    '20148001',
    '21473001',
    '25056001',
    '26198001',
    '29075001',
    '30189001',
    '31069001',
    '33281001',
    '35281001',
    '36063001',
    '44020001',
    '45055001',
    '47091001',
    '51183001',
    '51449002',
    '54526001',
    '58160001',
    '59343001',
    '63113001',
    '64549001',
    '66136001',
    '67124001',
    '69029001',
    '72181001',
    '73054001',
    '75114001',
    '86027001'
);

CREATE OR REPLACE VIEW public.v_itn_daily_1991_2020_real AS

WITH quotidienne_1991_2020 AS (
    SELECT
        "NUM_POSTE" AS station_code,
        "AAAAMMJJ" AS date,
        "TNTXM" AS tntxm
    FROM public."Quotidienne"
    WHERE '1991-01-01T00:00:00+00:00' <= "AAAAMMJJ" AND "AAAAMMJJ" < '2021-01-01T00:00:00+00:00'
        AND "TNTXM" IS NOT NULL
        AND "NUM_POSTE" IN (
            SELECT station_code FROM v_station_itn
        )
),
source AS (
    SELECT
        q.station_code AS station_code,
        q.date AS date,
        q.tntxm AS tntxm
    FROM quotidienne_1991_2020 q
),
normalized AS (
    SELECT *
    FROM source
    WHERE NOT (
        station_code = CASE
            WHEN date < '2012-05-08T00:00:00+00:00' THEN '51449002'
            ELSE '51183001'
        END
    )
),
distinct_dates AS (
    SELECT DISTINCT date
    FROM normalized
),
stations_without_reims AS (
    SELECT station_code
    FROM public.v_station_itn
    WHERE station_code NOT IN ('51183001', '51449002')
),
expected_by_day AS (
    SELECT
        d.date,
        swr.station_code
    FROM distinct_dates d
    CROSS JOIN stations_without_reims swr

    UNION ALL

    SELECT
        d.date,
        CASE
            WHEN d.date < '2012-05-08T00:00:00+00:00' THEN '51183001'
            ELSE '51449002'
        END AS station_code
    FROM distinct_dates d
),
present AS (
    SELECT DISTINCT
        date,
        station_code
    FROM normalized
),
valid_days AS (
    SELECT d.date
    FROM distinct_dates d
    LEFT JOIN (
        SELECT
            e.date,
            COUNT(*) AS missing_count
        FROM expected_by_day e
        LEFT JOIN present p
            ON p.date = e.date
                AND p.station_code = e.station_code
        WHERE p.station_code IS NULL
        GROUP BY e.date
    ) m ON m.date = d.date
    LEFT JOIN (
        SELECT
            p.date,
            COUNT(*) AS unexpected_count
        FROM present p
        LEFT JOIN expected_by_day e
            ON e.date = p.date
                AND e.station_code = p.station_code
        WHERE e.station_code IS NULL
        GROUP BY p.date
    ) u ON u.date = d.date
    LEFT JOIN (
        SELECT
            date,
            COUNT(*) AS normalized_station_count
        FROM present
        GROUP BY date
    ) c ON c.date = d.date
    WHERE COALESCE(m.missing_count, 0) = 0
        AND COALESCE(u.unexpected_count, 0) = 0
        AND COALESCE(c.normalized_station_count, 0) = 30
)
SELECT
    n.date AS date,
    EXTRACT(YEAR  FROM n.date)::int AS year,
    EXTRACT(MONTH FROM n.date)::int AS month,
    EXTRACT(DAY   FROM n.date)::int AS day_of_month,
    FALSE AS is_fictive,
    AVG(n.tntxm) AS itn
FROM normalized n
    INNER JOIN valid_days v
        ON v.date = n.date
GROUP BY n.date;

CREATE MATERIALIZED VIEW public.mv_itn_daily_1991_2020_real AS
SELECT
    date,
    year,
    month,
    day_of_month,
    is_fictive,
    itn
FROM public.v_itn_daily_1991_2020_real
ORDER BY date;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_itn_daily_1991_2020_real_date
    ON public.mv_itn_daily_1991_2020_real (date);

CREATE INDEX IF NOT EXISTS idx_mv_itn_daily_1991_2020_real_month_day
    ON public.mv_itn_daily_1991_2020_real (month, day_of_month);

CREATE INDEX IF NOT EXISTS idx_mv_itn_daily_1991_2020_real_year
    ON public.mv_itn_daily_1991_2020_real (year);

CREATE OR REPLACE VIEW public.v_itn_daily_1991_2020_with_feb29 AS
WITH feb29_fictive AS (
    SELECT
        NULL::date AS date,
        feb28.year,
        2 AS month,
        29 AS day_of_month,
        TRUE AS is_fictive,
        ((feb28.itn + mar01.itn) / 2.0) AS itn
    FROM public.mv_itn_daily_1991_2020_real feb28
    INNER JOIN public.mv_itn_daily_1991_2020_real mar01
        ON mar01.year = feb28.year
       AND mar01.month = 3
       AND mar01.day_of_month = 1
    WHERE feb28.month = 2
      AND feb28.day_of_month = 28
      AND NOT (
          (feb28.year % 4 = 0 AND feb28.year % 100 <> 0)
          OR (feb28.year % 400 = 0)
      )
)
SELECT *
FROM (
    SELECT * FROM public.mv_itn_daily_1991_2020_real
    UNION ALL
    SELECT * FROM feb29_fictive
) x;

CREATE OR REPLACE VIEW public.v_itn_baseline_daily_1991_2020 AS
SELECT
    month,
    day_of_month,
    COUNT(*)::int AS sample_size,
    AVG(itn) AS itn_mean,
    STDDEV_POP(itn) AS itn_stddev,
    PERCENTILE_CONT(0.2) WITHIN GROUP (ORDER BY itn) AS itn_p20,
    PERCENTILE_CONT(0.8) WITHIN GROUP (ORDER BY itn) AS itn_p80
FROM public.v_itn_daily_1991_2020_with_feb29
GROUP BY month, day_of_month;

CREATE OR REPLACE VIEW public.v_itn_baseline_monthly_1991_2020 AS
WITH monthly_series AS (
    SELECT
        year,
        month,
        AVG(itn) AS monthly_itn
    FROM public.v_itn_daily_1991_2020_with_feb29
    GROUP BY year, month
)
SELECT
    month,
    COUNT(*)::int AS sample_size,
    AVG(monthly_itn) AS itn_mean,
    STDDEV_POP(monthly_itn) AS itn_stddev,
    PERCENTILE_CONT(0.2) WITHIN GROUP (ORDER BY monthly_itn) AS itn_p20,
    PERCENTILE_CONT(0.8) WITHIN GROUP (ORDER BY monthly_itn) AS itn_p80
FROM monthly_series
GROUP BY month;

CREATE OR REPLACE VIEW public.v_itn_baseline_yearly_1991_2020 AS
WITH yearly_series AS (
    SELECT
        year,
        AVG(itn) AS yearly_itn
    FROM public.v_itn_daily_1991_2020_with_feb29
    GROUP BY year
)
SELECT
    COUNT(*)::int AS sample_size,
    AVG(yearly_itn) AS itn_mean,
    STDDEV_POP(yearly_itn) AS itn_stddev,
    PERCENTILE_CONT(0.2) WITHIN GROUP (ORDER BY yearly_itn) AS itn_p20,
    PERCENTILE_CONT(0.8) WITHIN GROUP (ORDER BY yearly_itn) AS itn_p80
FROM yearly_series;

CREATE OR REPLACE VIEW public.v_itn_daily_all_years AS
WITH source AS (
    SELECT
        q.station_code AS station_code,
        q.date,
        q.tntxm        AS tntxm
    FROM public.v_quotidienne q
    WHERE q.station_code IN (
        SELECT station_code FROM public.v_station_itn
    )
    AND q.date >= '1947-01-01T00:00:00+00:00'
),
normalized AS (
    SELECT *
    FROM source
    WHERE NOT (
        station_code = CASE
            WHEN date < '2012-05-08T00:00:00+00:00' THEN '51449002'
            ELSE '51183001'
        END
    )
)
SELECT
    n.date,
    EXTRACT(YEAR  FROM n.date)::int AS year,
    EXTRACT(MONTH FROM n.date)::int AS month,
    EXTRACT(DAY   FROM n.date)::int AS day_of_month,
    FALSE                           AS is_fictive,
    AVG(n.tntxm)                    AS itn
FROM normalized n
GROUP BY n.date
HAVING COUNT(DISTINCT n.station_code) >= 29;

CREATE MATERIALIZED VIEW public.mv_itn_daily_all_years AS
SELECT
    date,
    year,
    month,
    day_of_month,
    is_fictive,
    itn
FROM public.v_itn_daily_all_years
ORDER BY date;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_itn_daily_all_years_date
    ON public.mv_itn_daily_all_years (date);

CREATE INDEX IF NOT EXISTS idx_mv_itn_daily_all_years_month_day
    ON public.mv_itn_daily_all_years (month, day_of_month);

CREATE INDEX IF NOT EXISTS idx_mv_itn_daily_all_years_year
    ON public.mv_itn_daily_all_years (year);

CREATE OR REPLACE VIEW public.v_itn_daily_all_years_with_feb29 AS
WITH feb29_fictive AS (
    SELECT
        NULL::date AS date,
        feb28.year,
        2          AS month,
        29         AS day_of_month,
        TRUE       AS is_fictive,
        (feb28.itn + mar01.itn) / 2.0 AS itn
    FROM public.mv_itn_daily_all_years feb28
        INNER JOIN public.mv_itn_daily_all_years mar01
            ON  mar01.year         = feb28.year
            AND mar01.month        = 3
            AND mar01.day_of_month = 1
    WHERE feb28.month        = 2
        AND feb28.day_of_month = 28
        AND NOT (
            (feb28.year % 4 = 0 AND feb28.year % 100 <> 0)
            OR (feb28.year % 400 = 0)
        )
)
SELECT *
FROM (
    SELECT * FROM public.mv_itn_daily_all_years
    UNION ALL
    SELECT * FROM feb29_fictive
) x;

CREATE OR REPLACE VIEW public.v_itn_absolute_extremes_daily AS
SELECT
    month,
    day_of_month,
    MIN(itn) AS absolute_min,
    MAX(itn) AS absolute_max
FROM public.v_itn_daily_all_years_with_feb29
GROUP BY month, day_of_month;

CREATE OR REPLACE VIEW public.v_itn_absolute_extremes_monthly AS
WITH monthly_itn AS (
    SELECT
        year,
        month,
        AVG(itn) AS monthly_mean
    FROM public.v_itn_daily_all_years_with_feb29
    WHERE NOT is_fictive AND make_date(year, month, 1) < date_trunc('month', NOW())
    GROUP BY year, month
)
SELECT
    month,
    MIN(monthly_mean) AS absolute_min,
    MAX(monthly_mean) AS absolute_max
FROM monthly_itn
GROUP BY month;

CREATE OR REPLACE VIEW public.v_itn_absolute_extremes_yearly AS
WITH yearly_itn AS (
    SELECT
        year,
        AVG(itn) AS yearly_mean
    FROM public.v_itn_daily_all_years_with_feb29
    WHERE NOT is_fictive AND year < EXTRACT(YEAR FROM NOW())
    GROUP BY year
)
SELECT
    MIN(yearly_mean) AS absolute_min,
    MAX(yearly_mean) AS absolute_max
FROM yearly_itn
HAVING MIN(yearly_mean) IS NOT NULL AND MAX(yearly_mean) IS NOT NULL;

CREATE OR REPLACE VIEW public.v_records_battus AS

WITH

tx_all AS (
    SELECT
        q."NUM_POSTE",
        q."AAAAMMJJ",
        q."TX" AS val,
        MAX(q."TX") OVER (
            PARTITION BY q."NUM_POSTE"
            ORDER BY q."AAAAMMJJ"
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prev_val
    FROM public."Quotidienne" q
    WHERE q."TX" IS NOT NULL
),

tn_all AS (
    SELECT
        q."NUM_POSTE",
        q."AAAAMMJJ",
        q."TN" AS val,
        MIN(q."TN") OVER (
            PARTITION BY q."NUM_POSTE"
            ORDER BY q."AAAAMMJJ"
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prev_val
    FROM public."Quotidienne" q
    WHERE q."TN" IS NOT NULL
),

tx_monthly AS (
    SELECT
        q."NUM_POSTE",
        q."AAAAMMJJ",
        q."TX" AS val,
        EXTRACT(MONTH FROM q."AAAAMMJJ")::int AS month_num,
        MAX(q."TX") OVER (
            PARTITION BY q."NUM_POSTE", EXTRACT(MONTH FROM q."AAAAMMJJ")
            ORDER BY q."AAAAMMJJ"
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prev_val
    FROM public."Quotidienne" q
    WHERE q."TX" IS NOT NULL
),

tn_monthly AS (
    SELECT
        q."NUM_POSTE",
        q."AAAAMMJJ",
        q."TN" AS val,
        EXTRACT(MONTH FROM q."AAAAMMJJ")::int AS month_num,
        MIN(q."TN") OVER (
            PARTITION BY q."NUM_POSTE", EXTRACT(MONTH FROM q."AAAAMMJJ")
            ORDER BY q."AAAAMMJJ"
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prev_val
    FROM public."Quotidienne" q
    WHERE q."TN" IS NOT NULL
),

tx_seasonal AS (
    SELECT
        q."NUM_POSTE",
        q."AAAAMMJJ",
        q."TX" AS val,
        CASE EXTRACT(MONTH FROM q."AAAAMMJJ")::int
            WHEN 12 THEN 'winter' WHEN 1 THEN 'winter' WHEN 2 THEN 'winter'
            WHEN  3 THEN 'spring' WHEN 4 THEN 'spring' WHEN 5 THEN 'spring'
            WHEN  6 THEN 'summer' WHEN 7 THEN 'summer' WHEN 8 THEN 'summer'
            WHEN  9 THEN 'autumn' WHEN 10 THEN 'autumn' WHEN 11 THEN 'autumn'
        END AS season_val,
        MAX(q."TX") OVER (
            PARTITION BY q."NUM_POSTE",
                CASE EXTRACT(MONTH FROM q."AAAAMMJJ")::int
                    WHEN 12 THEN 'winter' WHEN 1 THEN 'winter' WHEN 2 THEN 'winter'
                    WHEN  3 THEN 'spring' WHEN 4 THEN 'spring' WHEN 5 THEN 'spring'
                    WHEN  6 THEN 'summer' WHEN 7 THEN 'summer' WHEN 8 THEN 'summer'
                    WHEN  9 THEN 'autumn' WHEN 10 THEN 'autumn' WHEN 11 THEN 'autumn'
                END
            ORDER BY q."AAAAMMJJ"
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prev_val
    FROM public."Quotidienne" q
    WHERE q."TX" IS NOT NULL
),

tn_seasonal AS (
    SELECT
        q."NUM_POSTE",
        q."AAAAMMJJ",
        q."TN" AS val,
        CASE EXTRACT(MONTH FROM q."AAAAMMJJ")::int
            WHEN 12 THEN 'winter' WHEN 1 THEN 'winter' WHEN 2 THEN 'winter'
            WHEN  3 THEN 'spring' WHEN 4 THEN 'spring' WHEN 5 THEN 'spring'
            WHEN  6 THEN 'summer' WHEN 7 THEN 'summer' WHEN 8 THEN 'summer'
            WHEN  9 THEN 'autumn' WHEN 10 THEN 'autumn' WHEN 11 THEN 'autumn'
        END AS season_val,
        MIN(q."TN") OVER (
            PARTITION BY q."NUM_POSTE",
                CASE EXTRACT(MONTH FROM q."AAAAMMJJ")::int
                    WHEN 12 THEN 'winter' WHEN 1 THEN 'winter' WHEN 2 THEN 'winter'
                    WHEN  3 THEN 'spring' WHEN 4 THEN 'spring' WHEN 5 THEN 'spring'
                    WHEN  6 THEN 'summer' WHEN 7 THEN 'summer' WHEN 8 THEN 'summer'
                    WHEN  9 THEN 'autumn' WHEN 10 THEN 'autumn' WHEN 11 THEN 'autumn'
                END
            ORDER BY q."AAAAMMJJ"
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prev_val
    FROM public."Quotidienne" q
    WHERE q."TN" IS NOT NULL
)

SELECT
    'all_time'   AS period_type,
    NULL::text   AS period_value,
    'TX'         AS record_type,
    r."NUM_POSTE"    AS station_code,
    s.name           AS station_name,
    s.departement    AS department,
    r.val            AS record_value,
    r."AAAAMMJJ"     AS record_date
FROM tx_all r
JOIN public.v_station_records s ON s.station_code = r."NUM_POSTE"
WHERE (r.prev_val IS NULL OR r.val > r.prev_val)
  AND r."AAAAMMJJ" >= s.first_temperature_date + interval '50 years'

UNION ALL

SELECT
    'all_time'       AS period_type,
    NULL::text       AS period_value,
    'TN'             AS record_type,
    r."NUM_POSTE"    AS station_code,
    s.name           AS station_name,
    s.departement    AS department,
    r.val            AS record_value,
    r."AAAAMMJJ"     AS record_date
FROM tn_all r
JOIN public.v_station_records s ON s.station_code = r."NUM_POSTE"
WHERE (r.prev_val IS NULL OR r.val < r.prev_val)
  AND r."AAAAMMJJ" >= s.first_temperature_date + interval '50 years'

UNION ALL

SELECT
    'month'              AS period_type,
    r.month_num::text    AS period_value,
    'TX'                 AS record_type,
    r."NUM_POSTE"        AS station_code,
    s.name               AS station_name,
    s.departement        AS department,
    r.val                AS record_value,
    r."AAAAMMJJ"         AS record_date
FROM tx_monthly r
JOIN public.v_station_records s ON s.station_code = r."NUM_POSTE"
WHERE (r.prev_val IS NULL OR r.val > r.prev_val)
  AND r."AAAAMMJJ" >= s.first_temperature_date + interval '50 years'

UNION ALL

SELECT
    'month'              AS period_type,
    r.month_num::text    AS period_value,
    'TN'                 AS record_type,
    r."NUM_POSTE"        AS station_code,
    s.name               AS station_name,
    s.departement        AS department,
    r.val                AS record_value,
    r."AAAAMMJJ"         AS record_date
FROM tn_monthly r
JOIN public.v_station_records s ON s.station_code = r."NUM_POSTE"
WHERE (r.prev_val IS NULL OR r.val < r.prev_val)
  AND r."AAAAMMJJ" >= s.first_temperature_date + interval '50 years'

UNION ALL

SELECT
    'season'         AS period_type,
    r.season_val     AS period_value,
    'TX'             AS record_type,
    r."NUM_POSTE"    AS station_code,
    s.name           AS station_name,
    s.departement    AS department,
    r.val            AS record_value,
    r."AAAAMMJJ"     AS record_date
FROM tx_seasonal r
JOIN public.v_station_records s ON s.station_code = r."NUM_POSTE"
WHERE (r.prev_val IS NULL OR r.val > r.prev_val)
  AND r."AAAAMMJJ" >= s.first_temperature_date + interval '50 years'

UNION ALL

SELECT
    'season'         AS period_type,
    r.season_val     AS period_value,
    'TN'             AS record_type,
    r."NUM_POSTE"    AS station_code,
    s.name           AS station_name,
    s.departement    AS department,
    r.val            AS record_value,
    r."AAAAMMJJ"     AS record_date
FROM tn_seasonal r
JOIN public.v_station_records s ON s.station_code = r."NUM_POSTE"
WHERE (r.prev_val IS NULL OR r.val < r.prev_val)
  AND r."AAAAMMJJ" >= s.first_temperature_date + interval '50 years';

CREATE MATERIALIZED VIEW public.mv_records_battus AS
SELECT
    period_type,
    period_value,
    record_type,
    station_code,
    station_name,
    department,
    record_value,
    record_date
FROM public.v_records_battus;

CREATE INDEX IF NOT EXISTS idx_mv_records_battus_query
ON public.mv_records_battus (record_type, period_type, period_value);

CREATE INDEX IF NOT EXISTS idx_mv_records_battus_station
ON public.mv_records_battus (station_code);

CREATE OR REPLACE VIEW public.v_records_absolus_par_mois AS
WITH ranked AS (
    SELECT
        m.station_code,
        date,
        txx,
        tnn,
        ROW_NUMBER() OVER (
            PARTITION BY m.station_code, EXTRACT(MONTH FROM date)::int
            ORDER BY txx DESC NULLS LAST, date ASC
        ) AS rn_txx_max,
        ROW_NUMBER() OVER (
            PARTITION BY m.station_code, EXTRACT(MONTH FROM date)::int
            ORDER BY tnn ASC NULLS LAST, date ASC
        ) AS rn_tnn_min
    FROM public.v_mensuelle AS m
        INNER JOIN public.v_station_records AS s
            ON m.station_code = s.station_code
    WHERE txx IS NOT NULL OR tnn IS NOT NULL
)
SELECT
    station_code,
    EXTRACT(MONTH FROM date)::int AS month,
    MAX(CASE WHEN rn_txx_max = 1 THEN txx END) AS txx_max,
    MAX(CASE WHEN rn_txx_max = 1 THEN date END) AS txx_max_date,
    MAX(CASE WHEN rn_tnn_min = 1 THEN tnn END) AS tnn_min,
    MAX(CASE WHEN rn_tnn_min = 1 THEN date END) AS tnn_min_date
FROM ranked
GROUP BY station_code, EXTRACT(MONTH FROM date)::int;

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

CREATE OR REPLACE VIEW public.v_records_absolus_par_saison AS
WITH base AS (
    SELECT
        m.station_code,
        m.txx_max_date,
        m.tnn_min_date,
        m.txx_max,
        m.tnn_min,
        CASE
            WHEN m.month IN (12, 1, 2) THEN 1
            WHEN m.month IN (3, 4, 5) THEN 2
            WHEN m.month IN (6, 7, 8) THEN 3
            ELSE 4
        END AS season_id
    FROM public.mv_records_absolus_par_mois AS m
),
ranked AS (
    SELECT
        station_code,
        txx_max_date,
        tnn_min_date,
        txx_max,
        tnn_min,
        season_id,
        ROW_NUMBER() OVER (
            PARTITION BY station_code, season_id
            ORDER BY txx_max DESC NULLS LAST, txx_max_date ASC
        ) AS rn_txx_max,
        ROW_NUMBER() OVER (
            PARTITION BY station_code, season_id
            ORDER BY tnn_min ASC NULLS LAST, tnn_min_date ASC
        ) AS rn_tnn_min
    FROM base
)
SELECT
    station_code,
    CASE season_id
        WHEN 1 THEN 'winter'
        WHEN 2 THEN 'spring'
        WHEN 3 THEN 'summer'
        ELSE 'autumn'
    END AS season,
    MAX(CASE WHEN rn_txx_max = 1 THEN txx_max END) AS txx_max,
    MAX(CASE WHEN rn_txx_max = 1 THEN txx_max_date END) AS txx_max_date,
    MAX(CASE WHEN rn_tnn_min = 1 THEN tnn_min END) AS tnn_min,
    MAX(CASE WHEN rn_tnn_min = 1 THEN tnn_min_date END) AS tnn_min_date
FROM ranked
GROUP BY station_code, season_id;

CREATE OR REPLACE VIEW public.v_records_absolus AS
WITH ranked AS (
    SELECT
        station_code,
        txx_max_date,
        tnn_min_date,
        txx_max,
        tnn_min,
        ROW_NUMBER() OVER (
            PARTITION BY station_code
            ORDER BY txx_max DESC NULLS LAST, txx_max_date ASC
        ) AS rn_txx_max,
        ROW_NUMBER() OVER (
            PARTITION BY station_code
            ORDER BY tnn_min ASC NULLS LAST, tnn_min_date ASC
        ) AS rn_tnn_min
    FROM public.v_records_absolus_par_saison
)
SELECT
    station_code,
    MAX(CASE WHEN rn_txx_max = 1 THEN txx_max END) AS txx_max,
    MAX(CASE WHEN rn_txx_max = 1 THEN txx_max_date END) AS txx_max_date,
    MAX(CASE WHEN rn_tnn_min = 1 THEN tnn_min END) AS tnn_min,
    MAX(CASE WHEN rn_tnn_min = 1 THEN tnn_min_date END) AS tnn_min_date
FROM ranked
GROUP BY station_code;

CREATE OR REPLACE VIEW public.v_records_absolus_par_type AS

-- All-time chaud
SELECT
    'all_time'     AS period_type,
    NULL::text     AS period_value,
    'TX'           AS record_type,
    m.station_code AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    m.txx_max      AS record_value,
    m.txx_max_date AS record_date
FROM public.v_records_absolus m
    JOIN public.v_station_records s
        ON s.station_code = m.station_code

UNION ALL

-- All-time froid
SELECT
    'all_time'     AS period_type,
    NULL::text     AS period_value,
    'TN'           AS record_type,
    m.station_code AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    m.tnn_min      AS record_value,
    m.tnn_min_date AS record_date
FROM public.v_records_absolus m
    JOIN public.v_station_records s
        ON s.station_code = m.station_code

UNION ALL

-- Seasonal chaud
SELECT
    'season'       AS period_type,
    m.season::text AS period_value,
    'TX'           AS record_type,
    m.station_code AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    m.txx_max      AS record_value,
    m.txx_max_date AS record_date
FROM public.v_records_absolus_par_saison m
    JOIN public.v_station_records s
        ON s.station_code = m.station_code

UNION ALL

-- Seasonal froid
SELECT
    'season'       AS period_type,
    m.season::text AS period_value,
    'TN'           AS record_type,
    m.station_code AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    m.tnn_min      AS record_value,
    m.tnn_min_date AS record_date
FROM public.v_records_absolus_par_saison m
    JOIN public.v_station_records s
        ON s.station_code = m.station_code

UNION ALL

-- Monthly chaud
SELECT
    'month'        AS period_type,
    m.month::text  AS period_value,
    'TX'           AS record_type,
    m.station_code AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    m.txx_max      AS record_value,
    m.txx_max_date AS record_date
FROM public.mv_records_absolus_par_mois m
    JOIN public.v_station_records s
        ON s.station_code = m.station_code

UNION ALL

-- Monthly froid
SELECT
    'month'        AS period_type,
    m.month::text  AS period_value,
    'TN'           AS record_type,
    m.station_code AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    m.tnn_min      AS record_value,
    m.tnn_min_date AS record_date
FROM public.mv_records_absolus_par_mois m
    JOIN public.v_station_records s
        ON s.station_code = m.station_code;
