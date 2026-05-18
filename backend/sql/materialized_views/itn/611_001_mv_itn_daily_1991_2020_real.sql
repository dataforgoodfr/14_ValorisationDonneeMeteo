DROP MATERIALIZED VIEW IF EXISTS mv_itn_daily_1991_2020_real;

CREATE MATERIALIZED VIEW mv_itn_daily_1991_2020_real AS

SELECT
     date,
     year,
     month,
     day_of_month,
     is_fictive,
     itn
FROM v_itn_daily_1991_2020_real
ORDER BY date;

CREATE UNIQUE INDEX idx_mv_itn_daily_1991_2020_real_date
    ON mv_itn_daily_1991_2020_real (date);

CREATE INDEX idx_mv_itn_daily_1991_2020_real_month_day
    ON mv_itn_daily_1991_2020_real (month, day_of_month);

CREATE INDEX idx_mv_itn_daily_1991_2020_real_year
    ON mv_itn_daily_1991_2020_real (year);
