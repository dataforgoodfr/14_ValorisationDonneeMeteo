CREATE OR REPLACE VIEW public.v_station_classe_3 AS
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
    s.date_de_creation,
    s.date_de_fermeture,
    s.first_temperature_date
FROM public.v_station_classe_4 s
WHERE s.classe_recente <= 3
ORDER BY s.station_code;
