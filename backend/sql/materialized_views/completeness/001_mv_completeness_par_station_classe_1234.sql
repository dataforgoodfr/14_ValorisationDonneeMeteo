DROP MATERIALIZED VIEW IF EXISTS public.mv_completeness_par_station_classe_1234;

CREATE MATERIALIZED VIEW public.mv_completeness_par_station_classe_1234 AS
WITH params AS (
    SELECT
        DATE '1806-01-01' AS date_debut,
        DATE '2026-12-31' AS date_fin
)
SELECT
    sc.station_code,
    ROUND(
        SUM(
            LEAST(COALESCE(sc.date_fin::date, p.date_fin), p.date_fin)
            - GREATEST(sc.date_debut::date, p.date_debut)
        )::numeric
        /
        MAX(p.date_fin - p.date_debut),
        2
    ) AS completeness

FROM public.v_station_classe_retroactive sc
CROSS JOIN params p
WHERE sc.date_debut <= p.date_fin
AND (sc.date_fin IS NULL OR sc.date_fin >= p.date_debut) AND sc.classe < 5
GROUP BY sc.station_code;
