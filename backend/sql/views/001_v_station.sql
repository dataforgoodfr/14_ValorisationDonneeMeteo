CREATE OR REPLACE VIEW public.v_station AS
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
  scr.classe AS classe_recente,
  scd."annee_de_creation" AS annee_de_creation,
  scd."annee_de_fermeture" AS annee_de_fermeture
FROM public."Station" s
 JOIN public."station_creation_date" scd
  ON s."id" = scd."station_code"
 LEFT JOIN station_classe_recente scr
  ON s."id" = scr."station_code"
ORDER BY s."id";
