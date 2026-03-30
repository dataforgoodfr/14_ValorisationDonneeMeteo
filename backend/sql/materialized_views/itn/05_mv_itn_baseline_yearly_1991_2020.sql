DROP MATERIALIZED VIEW IF EXISTS mv_itn_baseline_yearly_1991_2020;

CREATE MATERIALIZED VIEW mv_itn_baseline_yearly_1991_2020 AS
WITH yearly_series AS (
    SELECT
        year,
        AVG(itn) AS yearly_itn
    FROM mv_itn_daily_1991_2020_with_feb29
    GROUP BY year
)
SELECT
    COUNT(*)::int AS sample_size,
    AVG(yearly_itn) AS itn_mean,
    STDDEV_POP(yearly_itn) AS itn_stddev,
    PERCENTILE_CONT(0.2) WITHIN GROUP (ORDER BY yearly_itn) AS itn_p20,
    PERCENTILE_CONT(0.8) WITHIN GROUP (ORDER BY yearly_itn) AS itn_p80
FROM yearly_series;
