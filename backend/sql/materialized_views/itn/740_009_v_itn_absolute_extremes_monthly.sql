-- Vue : extremes absolus de l'ITN par mois (minimum et maximum des moyennes mensuelles).
-- Le filtrage >= 1947 est effectué en amont dans mv_itn_daily_all_years.
-- Les jours fictifs (29 fév synthétique) sont exclus : la moyenne mensuelle ne porte que sur
-- les jours réels, cohérence avec le calcul de la température observée dans le service.
CREATE OR REPLACE VIEW public.v_itn_absolute_extremes_monthly AS
WITH monthly_itn AS (
    SELECT
        year,
        month,
        AVG(itn) AS monthly_mean
    FROM public.v_itn_daily_all_years_with_feb29
    WHERE NOT is_fictive AND make_date(year, month, 1) < date_trunc('month', NOW())
    GROUP BY year, month
)
SELECT
    month,
    MIN(monthly_mean) AS absolute_min,
    MAX(monthly_mean) AS absolute_max
FROM monthly_itn
GROUP BY month;
