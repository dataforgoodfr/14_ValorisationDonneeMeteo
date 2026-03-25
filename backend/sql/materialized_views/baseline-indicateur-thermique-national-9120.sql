/*
===============================================================================
BASELINE DE L’INDICATEUR THERMIQUE NATIONAL (1991–2020)
===============================================================================

OBJECTIF
--------
Calculer la température moyenne journalière à base du(TNTXM),
température minimum (TN),
température maximum (TM), la veleur de l'écart type base et la valeur de
l'écart type haute de l’année (month, day), sur la période de référence
1991–2020.

Le résultat est une baseline de l'indicateur thermique national

SORTIE
------
Pour chaque (month, day) :
- baseline_mean_temperature : moyenne des TNTXM durant les jours de l'année
- baseline_min_temperature : TNTXM minimum pour une journée à travers les
différente station
- baseline_max_temperature : TNTXM maximum pour une journée à travers les
différente station
- baseline_stdev_lower_temperature : écart type haut de l'ensemble des
TNTXM de la journée
- baseline_stdev_upper_temperature : écart type bas de l'ensemble des
TNTXM de la journée


RÈGLES MÉTIER
-------------
- Gestion du 29 février.
- Traitement des données manquantes :
- Seuil minimal de données pour calculer une moyenne
- Cohérence avec la définition officielle de l’ITN.

PÉRIMÈTRE
---------
- Période : [1991-01-01, 2020-12-31]

SOURCES
-------
- v_quotidienne_itn :
    - date
    - tntxm (température max journalière)


STRUCTURE DE LA REQUÊTE
-----------------------

1. gestion de la station Reims - Courcy  et  Reims - Prunay

2. base :

    besoin : température moyenne, température max, témepérature minimum
    l'écart type de temperature

    - extraction des données sur la période de référence
    - dérivation year / month / day


2. agrégation finale :
    - moyenne par station par jour
    - minimum par et par jour
    - maximum par station et par jour
    - écart type basse par station et par jour
    - écart type haut par station et par jour


POINTS DE VIGILANCE
-------------------
- Cohérence des station_code entre v_quotidienne_itn et v_station
- Complétude des données autour du 28/02 et 01/03
- Hypothèse implicite : TNTXM disponible et fiable sur toute la période
-

===============================================================================
*/


SELECT
    EXTRACT(MONTH FROM v.date)::int AS month,
    EXTRACT(DAY   FROM v.date)::int AS day,
    AVG(v.tntxm) AS baseline_mean_temperature,
    MIN(v.tntxm) AS baseline_min_temperature,
    MAX(v.tntxm) AS baseline_max_temperature,
    AVG(v.tntxm) - STDDEV_SAMP(v.tntxm) AS baseline_stdev_lower_temperature,
    AVG(v.tntxm) - STDDEV_SAMP(v.tntxm) AS baseline_stdev_upper_temperature
FROM public.v_quotidienne_itn v
WHERE v.date >= DATE '1991-01-01'
    AND v.date <  DATE '2020-12-31'
GROUP BY v.date;
