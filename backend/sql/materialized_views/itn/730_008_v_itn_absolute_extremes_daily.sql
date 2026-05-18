-- Vue : extremes absolus de l'ITN par jour calendaire (mois + jour du mois).
-- Le filtrage >= 1947 est effectué en amont dans mv_itn_daily_all_years.
CREATE OR REPLACE VIEW public.v_itn_absolute_extremes_daily AS
SELECT
    month,
    day_of_month,
    MIN(itn) AS absolute_min,
    MAX(itn) AS absolute_max
FROM public.v_itn_daily_all_years_with_feb29
GROUP BY month, day_of_month;
