DROP MATERIALIZED VIEW IF EXISTS mv_itn_baseline_1991_2020;

CREATE MATERIALIZED VIEW mv_itn_baseline_1991_2020 AS
SELECT
    climatology_day,
    month,
    day_of_month,
    COUNT(*)::int AS sample_size,
    AVG(itn)::double precision AS itn_mean,
    STDDEV_POP(itn)::double precision AS itn_stddev,
    PERCENTILE_CONT(0.2) WITHIN GROUP (ORDER BY itn)::double precision AS itn_p20,
    PERCENTILE_CONT(0.8) WITHIN GROUP (ORDER BY itn)::double precision AS itn_p80
FROM mv_itn_daily_1991_2020_with_feb29
GROUP BY climatology_day, month, day_of_month
ORDER BY climatology_day;

CREATE UNIQUE INDEX idx_mv_itn_baseline_1991_2020_climatology_day
    ON mv_itn_baseline_1991_2020 (climatology_day);

CREATE UNIQUE INDEX idx_mv_itn_baseline_1991_2020_month_day
    ON mv_itn_baseline_1991_2020 (month, day_of_month);
