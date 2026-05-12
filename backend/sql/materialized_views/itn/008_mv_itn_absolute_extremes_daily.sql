-- Vue matérialisée : extremes absolus de l'ITN par jour calendaire (mois + jour du mois).
-- Le filtrage >= 1946 est effectué en amont dans mv_itn_daily_all_years.
DROP MATERIALIZED VIEW IF EXISTS mv_itn_absolute_extremes_daily;

CREATE MATERIALIZED VIEW mv_itn_absolute_extremes_daily AS
SELECT
    month,
    day_of_month,
    MIN(itn) AS absolute_min,
    MAX(itn) AS absolute_max
FROM mv_itn_daily_all_years_with_feb29
GROUP BY month, day_of_month
ORDER BY month, day_of_month;

CREATE UNIQUE INDEX idx_mv_itn_absolute_extremes_daily_month_day
    ON mv_itn_absolute_extremes_daily (month, day_of_month);
