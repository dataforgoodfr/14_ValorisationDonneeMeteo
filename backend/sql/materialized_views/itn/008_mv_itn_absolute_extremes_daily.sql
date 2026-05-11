-- Vue matérialisée : extremes absolus de l'ITN par jour calendaire (mois + jour du mois).
-- Couvre les années >= 1946 (début de disponibilité fiable des données ITN).
DROP MATERIALIZED VIEW IF EXISTS mv_itn_absolute_extremes_daily;

CREATE MATERIALIZED VIEW mv_itn_absolute_extremes_daily AS
SELECT
    month,
    day_of_month,
    MIN(itn) AS absolute_min,
    MAX(itn) AS absolute_max
FROM mv_itn_daily_all_years_with_feb29
WHERE year >= 1946
GROUP BY month, day_of_month
ORDER BY month, day_of_month;

CREATE UNIQUE INDEX idx_mv_itn_absolute_extremes_daily_month_day
    ON mv_itn_absolute_extremes_daily (month, day_of_month);
