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
- Stations : uniquement celles avec classe_recente <= 4 (via v_station_deviation)

SOURCES
-------
- quotidienne_1991_2020 :
    - station_code
    - date
    - tntxm (température max journalière)
- v_station_deviation :
    - station_code

STRUCTURE DE LA REQUÊTE
-----------------------
1. base :
    - extraction des données sur la période de référence
    - filtrage des stations (classe_recente <= 4)
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
- Cohérence des station_code entre quotidienne_1991_2020 et v_station_deviation
- Complétude des données autour du 28/02 et 01/03
- Hypothèse implicite : TNTXM disponible et fiable sur toute la période

===============================================================================
*/

DROP MATERIALIZED VIEW IF EXISTS public.mv_baseline_station_daily_mean_1991_2020;

CREATE MATERIALIZED VIEW public.mv_baseline_station_daily_mean_1991_2020 AS
SELECT
    station_code,
    month,
    day,
    sample_count,
    baseline_mean_tntxm
FROM public.v_baseline_station_daily_mean_1991_2020;

-- ============================================================================
-- INDEX
-- ============================================================================

CREATE INDEX idx_mv_baseline_station_daily_mean
ON public.mv_baseline_station_daily_mean_1991_2020 (station_code, month, day);
