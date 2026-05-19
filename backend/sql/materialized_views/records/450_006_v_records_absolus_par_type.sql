-- DROP VIEW IF EXISTS public.v_records_absolus_par_type;

CREATE OR REPLACE VIEW public.v_records_absolus_par_type AS

-- All-time chaud
SELECT
    'all_time'     AS period_type,
    NULL::text     AS period_value,
    'TX'           AS record_type,
    m.station_code AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    m.txx_max      AS record_value,
    m.txx_max_date AS record_date
FROM public.v_records_absolus m
    JOIN public.v_station_records s
        ON s.station_code = m.station_code

UNION ALL

-- All-time froid
SELECT
    'all_time'     AS period_type,
    NULL::text     AS period_value,
    'TN'           AS record_type,
    m.station_code AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    m.tnn_min      AS record_value,
    m.tnn_min_date AS record_date
FROM public.v_records_absolus m
    JOIN public.v_station_records s
        ON s.station_code = m.station_code

UNION ALL

-- Seasonal chaud
SELECT
    'season'       AS period_type,
    m.season::text AS period_value,
    'TX'           AS record_type,
    m.station_code AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    m.txx_max      AS record_value,
    m.txx_max_date AS record_date
FROM public.v_records_absolus_par_saison m
    JOIN public.v_station_records s
        ON s.station_code = m.station_code

UNION ALL

-- Seasonal froid
SELECT
    'season'       AS period_type,
    m.season::text AS period_value,
    'TN'           AS record_type,
    m.station_code AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    m.tnn_min      AS record_value,
    m.tnn_min_date AS record_date
FROM public.v_records_absolus_par_saison m
    JOIN public.v_station_records s
        ON s.station_code = m.station_code

UNION ALL

-- Monthly chaud
SELECT
    'month'        AS period_type,
    m.month::text  AS period_value,
    'TX'           AS record_type,
    m.station_code AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    m.txx_max      AS record_value,
    m.txx_max_date AS record_date
FROM public.mv_records_absolus_par_mois m
    JOIN public.v_station_records s
        ON s.station_code = m.station_code

UNION ALL

-- Monthly froid
SELECT
    'month'        AS period_type,
    m.month::text  AS period_value,
    'TN'           AS record_type,
    m.station_code AS station_code,
    s.name         AS station_name,
    s.departement  AS department,
    m.tnn_min      AS record_value,
    m.tnn_min_date AS record_date
FROM public.mv_records_absolus_par_mois m
    JOIN public.v_station_records s
        ON s.station_code = m.station_code;
