DROP MATERIALIZED VIEW IF EXISTS mv_itn_baseline_monthly_1991_2020;

CREATE MATERIALIZED VIEW mv_itn_baseline_monthly_1991_2020 AS
WITH monthly_series AS (
    SELECT
        year,
        month,
        AVG(itn) AS monthly_itn
    FROM mv_itn_daily_1991_2020_with_feb29
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
GROUP BY month
ORDER BY month;

CREATE UNIQUE INDEX idx_mv_itn_baseline_monthly_1991_2020_month
    ON mv_itn_baseline_monthly_1991_2020 (month);
