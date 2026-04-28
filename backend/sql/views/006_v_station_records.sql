CREATE OR REPLACE VIEW public.v_station_records AS
SELECT
    s.station_code,
    s.name,
    s.departement,
    s.is_open,
    s.station_type,
    s.lon,
    s.lat,
    s.alt,
    s.is_public,
    s.classe_recente,
    s.annee_de_creation,
    s.annee_de_fermeture
FROM public.v_station_classe_3 s
ORDER BY s.station_code;
