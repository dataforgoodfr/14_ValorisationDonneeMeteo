CREATE OR REPLACE VIEW public.v_itn_daily_1991_2020_real AS

WITH quotidienne_1991_2020 AS (
    SELECT
        "NUM_POSTE" AS station_code,
        "AAAAMMJJ" AS date,
        "TNTXM" AS tntxm
    FROM "Quotidienne"
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
