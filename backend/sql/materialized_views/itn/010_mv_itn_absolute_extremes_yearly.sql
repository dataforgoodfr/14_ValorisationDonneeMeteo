-- Vue matérialisée : extremes absolus annuels de l'ITN (ligne unique).
-- Le filtrage >= 1946 est effectué en amont dans mv_itn_daily_all_years.
-- Les jours fictifs (29 fév synthétique) sont exclus : la moyenne annuelle ne porte que sur
-- les jours réels, cohérence avec le calcul de la température observée dans le service.
DROP MATERIALIZED VIEW IF EXISTS mv_itn_absolute_extremes_yearly;

CREATE MATERIALIZED VIEW mv_itn_absolute_extremes_yearly AS
WITH yearly_itn AS (
    SELECT
        year,
        AVG(itn) AS yearly_mean
    FROM mv_itn_daily_all_years_with_feb29
    WHERE NOT is_fictive
    GROUP BY year
)
SELECT
    MIN(yearly_mean) AS absolute_min,
    MAX(yearly_mean) AS absolute_max
FROM yearly_itn;
