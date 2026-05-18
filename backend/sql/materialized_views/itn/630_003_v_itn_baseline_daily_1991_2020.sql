CREATE OR REPLACE VIEW public.v_itn_baseline_daily_1991_2020 AS
SELECT
    month,
    day_of_month,
    COUNT(*)::int AS sample_size,
    AVG(itn) AS itn_mean,
    STDDEV_POP(itn) AS itn_stddev,
    PERCENTILE_CONT(0.2) WITHIN GROUP (ORDER BY itn) AS itn_p20,
    PERCENTILE_CONT(0.8) WITHIN GROUP (ORDER BY itn) AS itn_p80
FROM public.v_itn_daily_1991_2020_with_feb29
GROUP BY month, day_of_month;
