CREATE OR REPLACE VIEW public.v_station AS
SELECT
  s."id"::text               AS station_code,   -- PK côté Django
  s."nom"                    AS name,
  s."departement"            AS departement,
  s."frequence"              AS frequency,
  s."posteOuvert"            AS is_open,
  s."typePoste"              AS station_type,
  s."lon"                    AS lon,
  s."lat"                    AS lat,
  s."alt"                    AS alt,
  s."postePublic"            AS is_public,
  s."createdAt"              AS created_at,
  s."updatedAt"              AS updated_at
FROM public."Station" s
WHERE s."frequence" = 'horaire';
