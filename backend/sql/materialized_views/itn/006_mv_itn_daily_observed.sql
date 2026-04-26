DROP MATERIALIZED VIEW IF EXISTS mv_itn_daily_observed;

CREATE MATERIALIZED VIEW mv_itn_daily_observed AS
WITH source AS (
    SELECT
        q.station_code,
        q.date::date AS date,
        q.tntxm
    FROM public.v_quotidienne_itn q
    WHERE q.station_code IN (
        '47091001', '20148001', '25056001', '33281001', '73054001',
        '29075001', '14137001', '36063001', '63113001', '16089001',
        '21473001', '72181001', '59343001', '69029001', '13054001',
        '26198001', '54526001', '44020001', '58160001', '06088001',
        '30189001', '45055001', '75114001', '64549001', '66136001',
        '86027001', '35281001', '67124001', '31069001',
        '51183001', '51449002'
    )
    AND q.tntxm IS NOT NULL
),
normalized AS (
    SELECT
        date,
        CASE
            WHEN station_code IN ('51183001', '51449002') THEN
                CASE
                    WHEN date >= DATE '2012-05-08' THEN '51449002'
                    ELSE '51183001'
                END
            ELSE station_code
        END AS station_code,
        tntxm
    FROM source
),
daily_station_values AS (
    SELECT
        date,
        station_code,
        AVG(tntxm)::double precision AS tntxm
    FROM normalized
    GROUP BY date, station_code
),
valid_days AS (
    SELECT
        date
    FROM daily_station_values
    GROUP BY date
    HAVING COUNT(*) = 30
)
SELECT
    d.date,
    EXTRACT(YEAR FROM d.date)::int AS year,
    EXTRACT(MONTH FROM d.date)::int AS month,
    EXTRACT(DAY FROM d.date)::int AS day_of_month,
    AVG(d.tntxm)::double precision AS temperature
FROM daily_station_values d
JOIN valid_days v
    ON v.date = d.date
GROUP BY d.date
ORDER BY d.date;

CREATE UNIQUE INDEX idx_mv_itn_daily_observed_date
    ON mv_itn_daily_observed (date);

CREATE INDEX idx_mv_itn_daily_observed_year
    ON mv_itn_daily_observed (year);

CREATE INDEX idx_mv_itn_daily_observed_month_day
    ON mv_itn_daily_observed (month, day_of_month);
