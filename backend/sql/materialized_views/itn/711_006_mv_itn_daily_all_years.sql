-- Vue matérialisée : ITN journalier sur toutes les années disponibles (>= 1946).
-- Équivalent de 610_001_mv_itn_daily_1991_2020_real.sql sans la restriction de période.
-- Accepte les jours avec au moins 29 stations sur 30 (HAVING COUNT >= 29).
-- Le filtre date >= 1946-01-01 est appliqué ici sur la colonne indexée de v_quotidienne.
DROP MATERIALIZED VIEW IF EXISTS public.mv_itn_daily_all_years;

CREATE MATERIALIZED VIEW public.mv_itn_daily_all_years AS
SELECT
    date,
    year,
    month,
    day_of_month,
    is_fictive,
    itn
FROM public.v_itn_daily_all_years
ORDER BY date;

CREATE UNIQUE INDEX idx_mv_itn_daily_all_years_date
    ON public.mv_itn_daily_all_years (date);

CREATE INDEX idx_mv_itn_daily_all_years_day_of_month
    ON public.mv_itn_daily_all_years (day_of_month);

CREATE INDEX idx_mv_itn_daily_all_years_month_day
    ON public.mv_itn_daily_all_years (month, day_of_month);

CREATE INDEX idx_mv_itn_daily_all_years_year
    ON public.mv_itn_daily_all_years (year);
