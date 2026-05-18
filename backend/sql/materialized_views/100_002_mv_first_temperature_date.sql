DROP MATERIALIZED VIEW IF EXISTS public.mv_first_temperature_date;

CREATE MATERIALIZED VIEW public.mv_first_temperature_date AS
SELECT
    "NUM_POSTE"   AS station_code,
    MIN("AAAAMM") AS first_temperature_date
FROM "Mensuelle"
WHERE "TM" IS NOT NULL
GROUP BY "NUM_POSTE"
ORDER BY "NUM_POSTE" ASC;

CREATE UNIQUE INDEX IF NOT EXISTS mv_first_temperature_date_uq
    ON mv_first_temperature_date (station_code);
