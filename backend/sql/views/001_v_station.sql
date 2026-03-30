CREATE OR REPLACE VIEW public.v_station AS
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
  s."createdAt" AS created_at,
  s."updatedAt" AS updated_at
FROM public."Station" s
ORDER BY s."id", s."frequence";
