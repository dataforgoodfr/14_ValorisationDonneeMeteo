-- Vue : extremes absolus annuels de l'ITN (ligne unique).
-- Le filtrage >= 1947 est effectué en amont dans mv_itn_daily_all_years.
-- Les jours fictifs (29 fév synthétique) sont exclus : la moyenne annuelle ne porte que sur
-- les jours réels, cohérence avec le calcul de la température observée dans le service.
CREATE OR REPLACE VIEW public.v_itn_absolute_extremes_yearly AS
WITH yearly_itn AS (
    SELECT
        year,
        AVG(itn) AS yearly_mean
    FROM public.v_itn_daily_all_years_with_feb29
    WHERE NOT is_fictive AND year < EXTRACT(YEAR FROM NOW())
    GROUP BY year
)
SELECT
    MIN(yearly_mean) AS absolute_min,
    MAX(yearly_mean) AS absolute_max
FROM yearly_itn
HAVING MIN(yearly_mean) IS NOT NULL AND MAX(yearly_mean) IS NOT NULL;
