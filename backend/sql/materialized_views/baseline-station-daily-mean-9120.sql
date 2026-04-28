/*
===============================================================================
BASELINE CLIMATOLOGIQUE PAR STATION (1991–2020)
===============================================================================

OBJECTIF
--------
Calculer la température moyenne journalière (TNTXM) par station et par jour
de l’année (month, day), sur la période de référence 1991–2020.

Le résultat est une baseline climatologique utilisée pour comparer les
températures observées (ex: anomalies, déviations).

SORTIE
------
Pour chaque (station_code, month, day) :
- sample_count : nombre de valeurs utilisées dans la moyenne
- baseline_mean_tntxm : moyenne de TNTXM sur la période

RÈGLES MÉTIER
-------------
- La baseline couvre tous les jours de l’année, y compris le 29 février.
- Pour les années bissextiles :
    → le 29 février réel est utilisé.
- Pour les années non bissextiles :
    → un 29 février synthétique est créé :
        valeur = moyenne de (28 février, 1er mars)
    → uniquement si les deux valeurs existent
    → sinon, pas de contribution pour cette année

PÉRIMÈTRE
---------
- Période : [1991-01-01, 2021-01-01)
- Stations : uniquement celles avec station_type < 4 (via v_station)

SOURCES
-------
- v_quotidienne_itn :
    - station_code
    - date
    - tntxm (température max journalière)
- v_station :
    - station_code
    - station_type

STRUCTURE DE LA REQUÊTE
-----------------------
1. base :
    - extraction des données sur la période de référence
    - filtrage des stations (station_type < 4)
    - dérivation year / month / day

2. normal_days :
    - tous les jours sauf 29 février

3. leap_feb29 :
    - 29 février réels (années bissextiles)

4. non_leap_feb29 :
    - 29 février synthétiques pour années non bissextiles
    - moyenne (28/02, 01/03)

5. normalized_daily :
    - union de toutes les contributions

6. agrégation finale :
    - moyenne par station et jour de l’année

PERFORMANCE
-----------
- Requête prévue pour être exécutée offline (pré-calcul baseline)
- Temps d’exécution typique : quelques secondes sur dataset complet
- Ne pas utiliser dans un endpoint temps réel

POINTS DE VIGILANCE
-------------------
- Cohérence des station_code entre v_quotidienne_itn et v_station
- Complétude des données autour du 28/02 et 01/03
- Hypothèse implicite : TNTXM disponible et fiable sur toute la période

===============================================================================
*/

DROP MATERIALIZED VIEW IF EXISTS public.baseline_station_daily_mean_1991_2020;

CREATE MATERIALIZED VIEW public.baseline_station_daily_mean_1991_2020 AS

WITH allowed_stations AS (
    SELECT s.station_code
    FROM public.v_station s
    WHERE s.station_type IS NOT NULL
      AND s.station_type < 4
),

base AS (
    SELECT
        v.station_code,
        v.date,
        v.tntxm,
        EXTRACT(YEAR  FROM v.date)::int AS year,
        EXTRACT(MONTH FROM v.date)::int AS month,
        EXTRACT(DAY   FROM v.date)::int AS day
    FROM public.v_quotidienne_itn v
    WHERE v.date >= DATE '1991-01-01'
      AND v.date <  DATE '2021-01-01'
      AND v.station_code IN (
          SELECT station_code FROM allowed_stations
      )
),

normal_days AS (
    SELECT
        b.station_code,
        b.year,
        b.month,
        b.day,
        b.tntxm AS daily_value
    FROM base b
    WHERE NOT (b.month = 2 AND b.day = 29)
),

leap_feb29 AS (
    SELECT
        b.station_code,
        b.year,
        2 AS month,
        29 AS day,
        b.tntxm AS daily_value
    FROM base b
    WHERE b.month = 2
      AND b.day = 29
),

non_leap_feb29 AS (
    SELECT
        x.station_code,
        x.year,
        2 AS month,
        29 AS day,
        CASE
            WHEN COUNT(*) = 2 THEN AVG(x.tntxm)
            ELSE NULL
        END AS daily_value
    FROM (
        SELECT station_code, year, tntxm
        FROM base
        WHERE month = 2 AND day = 28

        UNION ALL

        SELECT station_code, year, tntxm
        FROM base
        WHERE month = 3 AND day = 1
    ) x
    WHERE NOT (
        (x.year % 4 = 0 AND x.year % 100 <> 0)
        OR x.year % 400 = 0
    )
    GROUP BY x.station_code, x.year
),

normalized_daily AS (
    SELECT * FROM normal_days
    UNION ALL
    SELECT * FROM leap_feb29
    UNION ALL
    SELECT * FROM non_leap_feb29
    WHERE daily_value IS NOT NULL
)

SELECT
    nd.station_code,
    nd.month,
    nd.day,
    COUNT(nd.daily_value) AS sample_count,
    ROUND(AVG(nd.daily_value)::numeric, 2) AS baseline_mean_tntxm
FROM normalized_daily nd
GROUP BY
    nd.station_code,
    nd.month,
    nd.day
HAVING COUNT(nd.daily_value) >= 24;

-- ============================================================================
-- INDEX
-- ============================================================================

CREATE INDEX idx_baseline_station_daily_mean
ON public.baseline_station_daily_mean_1991_2020 (station_code, month, day);
