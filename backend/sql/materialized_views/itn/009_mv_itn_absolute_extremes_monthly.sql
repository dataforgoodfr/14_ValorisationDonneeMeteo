-- Vue matérialisée : extremes absolus de l'ITN par mois (minimum et maximum des moyennes mensuelles).
-- Couvre les années >= 1946 (début de disponibilité fiable des données ITN).
-- Les jours fictifs (29 fév synthétique) sont exclus : la moyenne mensuelle ne porte que sur
-- les jours réels, cohérence avec le calcul de la température observée dans le service.
DROP MATERIALIZED VIEW IF EXISTS mv_itn_absolute_extremes_monthly;

CREATE MATERIALIZED VIEW mv_itn_absolute_extremes_monthly AS
WITH monthly_itn AS (
    SELECT
        year,
        month,
        AVG(itn) AS monthly_mean
    FROM mv_itn_daily_all_years_with_feb29
    WHERE NOT is_fictive AND date >= DATE '1946-01-01'
    GROUP BY year, month
)
SELECT
    month,
    MIN(monthly_mean) AS absolute_min,
    MAX(monthly_mean) AS absolute_max
FROM monthly_itn
GROUP BY month
ORDER BY month;

CREATE UNIQUE INDEX idx_mv_itn_absolute_extremes_monthly_month
    ON mv_itn_absolute_extremes_monthly (month);
