WITH base AS (
    SELECT
        v.station_code,
        v.date,
        v.tntxm,
        EXTRACT(YEAR  FROM v.date) AS year,
        EXTRACT(MONTH FROM v.date) AS month,
        EXTRACT(DAY   FROM v.date) AS day
    FROM public.v_quotidienne_itn v
    WHERE v.date BETWEEN DATE '1991-01-01' AND DATE '2020-12-31'
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
        SELECT
            b.station_code,
            b.year,
            b.tntxm
        FROM base b
        WHERE b.month = 2
          AND b.day = 28

        UNION ALL

        SELECT
            b.station_code,
            b.year,
            b.tntxm
        FROM base b
        WHERE b.month = 3
          AND b.day = 1
    ) x
    WHERE NOT (
        (MOD(x.year, 4) = 0 AND MOD(x.year, 100) <> 0)
        OR MOD(x.year, 400) = 0
    )
    GROUP BY
        x.station_code,
        x.year
),

normalized_daily AS (
    SELECT * FROM normal_days
    UNION ALL
    SELECT * FROM leap_feb29
    UNION ALL
    SELECT * FROM non_leap_feb29 WHERE daily_value IS NOT NULL
)

SELECT
    nd.station_code,
    nd.month,
    nd.day,
    COUNT(nd.daily_value) AS sample_count,
    AVG(nd.daily_value)   AS baseline_mean_tntxm
FROM normalized_daily nd
GROUP BY
    nd.station_code,
    nd.month,
    nd.day
ORDER BY
    nd.station_code,
    nd.month,
    nd.day
