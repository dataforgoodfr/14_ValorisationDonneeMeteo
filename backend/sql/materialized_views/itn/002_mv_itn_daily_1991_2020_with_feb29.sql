DROP MATERIALIZED VIEW IF EXISTS mv_itn_daily_1991_2020_with_feb29;

CREATE MATERIALIZED VIEW mv_itn_daily_1991_2020_with_feb29 AS
WITH feb29_fictive AS (
    SELECT
        NULL::date AS date,
        feb28.year,
        2 AS month,
        29 AS day_of_month,
        TRUE AS is_fictive,
        ((feb28.itn + mar01.itn) / 2.0)::double precision AS itn
    FROM mv_itn_daily_1991_2020_real feb28
    INNER JOIN mv_itn_daily_1991_2020_real mar01
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
SELECT
    date,
    year,
    month,
    day_of_month,
    CASE
        WHEN month = 1  THEN day_of_month
        WHEN month = 2  THEN 31  + day_of_month
        WHEN month = 3  THEN 60  + day_of_month
        WHEN month = 4  THEN 91  + day_of_month
        WHEN month = 5  THEN 121 + day_of_month
        WHEN month = 6  THEN 152 + day_of_month
        WHEN month = 7  THEN 182 + day_of_month
        WHEN month = 8  THEN 213 + day_of_month
        WHEN month = 9  THEN 244 + day_of_month
        WHEN month = 10 THEN 274 + day_of_month
        WHEN month = 11 THEN 305 + day_of_month
        WHEN month = 12 THEN 335 + day_of_month
    END::int AS climatology_day,
    is_fictive,
    itn
FROM (
    SELECT * FROM mv_itn_daily_1991_2020_real
    UNION ALL
    SELECT * FROM feb29_fictive
) x
ORDER BY year, month, day_of_month, is_fictive;

CREATE INDEX idx_mv_itn_daily_1991_2020_with_feb29_year
    ON mv_itn_daily_1991_2020_with_feb29 (year);

CREATE INDEX idx_mv_itn_daily_1991_2020_with_feb29_month_day
    ON mv_itn_daily_1991_2020_with_feb29 (month, day_of_month);

CREATE INDEX idx_mv_itn_daily_1991_2020_with_feb29_clim_day
    ON mv_itn_daily_1991_2020_with_feb29 (climatology_day);
