DROP MATERIALIZED VIEW IF EXISTS mv_itn_daily_1991_2020_real;

CREATE MATERIALIZED VIEW mv_itn_daily_1991_2020_real AS
WITH source AS (
    SELECT
        q.station_code AS station_code,
        q.date AS day,
        q.tntxm AS tntxm
    FROM v_quotidienne_itn q
    WHERE q.date >= DATE '1991-01-01'
      AND q.date <  DATE '2021-01-01'
      AND q.station_code IN (
          '47091001','20148001','25056001','33281001','73054001',
          '29075001','14137001','36063001','63113001','16089001',
          '21473001','72181001','59343001','69029001','13054001',
          '26198001','54526001','44020001','58160001','06088001',
          '30189001','45055001','75114001','64549001','66136001',
          '86027001','35281001','67124001','31069001',
          '51183001','51449002'
      )
),
normalized AS (
    SELECT *
    FROM source
    WHERE NOT (
        station_code = CASE
            WHEN day < DATE '2012-05-08' THEN '51449002'
            ELSE '51183001'
        END
    )
),
expected_stations AS (
    SELECT station_code
    FROM (
        VALUES
            ('47091001'),('20148001'),('25056001'),('33281001'),('73054001'),
            ('29075001'),('14137001'),('36063001'),('63113001'),('16089001'),
            ('21473001'),('72181001'),('59343001'),('69029001'),('13054001'),
            ('26198001'),('54526001'),('44020001'),('58160001'),('06088001'),
            ('30189001'),('45055001'),('75114001'),('64549001'),('66136001'),
            ('86027001'),('35281001'),('67124001'),('31069001')
    ) AS t(station_code)
),
expected_by_day AS (
    SELECT
        d.day,
        e.station_code
    FROM (SELECT DISTINCT day FROM normalized) d
    CROSS JOIN expected_stations e

    UNION ALL

    SELECT
        d.day,
        CASE
            WHEN d.day < DATE '2012-05-08' THEN '51183001'
            ELSE '51449002'
        END AS station_code
    FROM (SELECT DISTINCT day FROM normalized) d
),
present AS (
    SELECT DISTINCT
        day,
        station_code
    FROM normalized
),
valid_days AS (
    SELECT d.day
    FROM (SELECT DISTINCT day FROM normalized) d
    LEFT JOIN (
        SELECT
            e.day,
            COUNT(*) AS missing_count
        FROM expected_by_day e
        LEFT JOIN present p
            ON p.day = e.day
           AND p.station_code = e.station_code
        WHERE p.station_code IS NULL
        GROUP BY e.day
    ) m ON m.day = d.day
    LEFT JOIN (
        SELECT
            p.day,
            COUNT(*) AS unexpected_count
        FROM present p
        LEFT JOIN expected_by_day e
            ON e.day = p.day
           AND e.station_code = p.station_code
        WHERE e.station_code IS NULL
        GROUP BY p.day
    ) u ON u.day = d.day
    LEFT JOIN (
        SELECT
            day,
            COUNT(*) AS normalized_station_count
        FROM present
        GROUP BY day
    ) c ON c.day = d.day
    WHERE COALESCE(m.missing_count, 0) = 0
      AND COALESCE(u.unexpected_count, 0) = 0
      AND COALESCE(c.normalized_station_count, 0) = 30
)
SELECT
    n.day AS date,
    EXTRACT(YEAR  FROM n.day)::int AS year,
    EXTRACT(MONTH FROM n.day)::int AS month,
    EXTRACT(DAY   FROM n.day)::int AS day_of_month,
    FALSE AS is_fictive,
    AVG(n.tntxm) AS itn
FROM normalized n
INNER JOIN valid_days v
    ON v.day = n.day
GROUP BY n.day
ORDER BY n.day;

CREATE UNIQUE INDEX idx_mv_itn_daily_1991_2020_real_date
    ON mv_itn_daily_1991_2020_real (date);

CREATE INDEX idx_mv_itn_daily_1991_2020_real_month_day
    ON mv_itn_daily_1991_2020_real (month, day_of_month);

CREATE INDEX idx_mv_itn_daily_1991_2020_real_year
    ON mv_itn_daily_1991_2020_real (year);
