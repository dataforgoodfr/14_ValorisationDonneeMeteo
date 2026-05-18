CREATE OR REPLACE VIEW public.v_station_qualifiee_hexagone AS
WITH station_classe_recente AS (
    SELECT station_code, classe
    FROM public."station_classe"
    WHERE date_fin IS NULL
)
SELECT DISTINCT ON (s."id")
    s."id" AS station_code,
    s."nom" AS name,
    s."departement" AS departement,
    s."posteOuvert" AS is_open,
    s."typePoste" AS station_type,
    s."lon" AS lon,
    s."lat" AS lat,
    s."alt" AS alt,
    s."postePublic" AS is_public,
    scr."classe" AS classe_recente,
    scd."date_de_creation" AS date_de_creation,
    scd."date_de_fermeture" AS date_de_fermeture,
    EXTRACT (YEAR FROM scd."date_de_creation")::int AS annee_de_creation,
    EXTRACT (YEAR FROM scd."date_de_fermeture")::int AS annee_de_fermeture,
    ftd."first_temperature_date" AS first_temperature_date
FROM public."Station" s
    JOIN public."station_creation_date" scd
        ON s."id" = scd."station_code"
    LEFT JOIN station_classe_recente scr
        ON s."id" = scr."station_code"
    JOIN public."mv_first_temperature_date" ftd
        ON s."id" = ftd."station_code"
WHERE s."typePoste" <= 3
    AND s.departement < '96';
