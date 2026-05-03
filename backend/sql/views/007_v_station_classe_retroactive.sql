CREATE OR REPLACE VIEW public.v_station_classe_retroactive AS
WITH premieres_dates_de_classements_des_stations AS (
    SELECT
        station_code,
        MIN(date_debut) AS premiere_date_de_classement
    FROM public."station_classe"
    GROUP BY station_code
)
SELECT
    sc."station_code",
    sc."classe",
    CASE
        WHEN sc."date_debut" = pdcs.premiere_date_de_classement
             AND scd."date_de_creation" IS NOT NULL
        THEN scd."date_de_creation"
        ELSE sc."date_debut"
    END AS date_debut,
    sc."date_fin"
FROM public."station_classe" sc
JOIN premieres_dates_de_classements_des_stations pdcs
    ON sc."station_code" = pdcs.station_code
LEFT JOIN public."station_creation_date" scd
    ON sc."station_code" = scd."station_code";
