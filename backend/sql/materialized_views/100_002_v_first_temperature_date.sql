CREATE OR REPLACE VIEW public.v_first_temperature_date AS
SELECT
    "NUM_POSTE"   AS station_code,
    MIN("AAAAMM") AS first_temperature_date
FROM "Mensuelle"
WHERE "TM" IS NOT NULL
GROUP BY "NUM_POSTE";
