DROP MATERIALIZED VIEW IF EXISTS mv_itn_daily_1991_2020_with_feb29;

CREATE MATERIALIZED VIEW mv_itn_daily_1991_2020_with_feb29 AS
WITH feb29_fictive AS (
    SELECT
        NULL::date AS date,
        feb28.year,
        2 AS month,
        29 AS day_of_month,
        TRUE AS is_fictive,
        ((feb28.itn + mar01.itn) / 2.0) AS itn
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
SELECT *
FROM (
    SELECT * FROM mv_itn_daily_1991_2020_real
    UNION ALL
    SELECT * FROM feb29_fictive
) x
ORDER BY year, month, day_of_month, is_fictive;
