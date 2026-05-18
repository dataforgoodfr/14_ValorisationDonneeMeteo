/*
===============================================================================
VUE MATÉRIALISÉE : RECORDS PROGRESSIFS PAR STATION
===============================================================================

OBJECTIF
--------
Pré-calculer les records progressifs de température (TX max, TN min) pour
chaque station et chaque type de période (all_time, month, season).

Un record progressif est une date où la station a dépassé toutes ses valeurs
précédentes pour la même période.

STRUCTURE
---------
Colonnes :
  - period_type  : 'all_time' | 'month' | 'season'
  - period_value : NULL (all_time) | '1'–'12' (month) | 'spring'/'summer'/'autumn'/'winter'
  - record_type  : 'TX' (chaud) | 'TN' (froid)
  - station_code : identifiant station
  - station_name : nom de la station
  - department   : numéro de département
  - record_value : valeur du record (°C)
  - record_date  : date du record

UTILISATION
-----------
L'endpoint /api/v1/temperature/records lit directement cette MV via
MaterializedTemperatureRecordsDataSource. La query devient un simple SELECT
avec filtres indexés.

RAFRAÎCHISSEMENT
----------------
Commande Django : python manage.py refresh_records_mv
À exécuter après chaque import de nouvelles données quotidiennes.

PERFORMANCE
-----------
- Création : quelques minutes sur dataset complet (opération offline)
- Lecture : < 10 ms (index sur record_type, period_type, period_value)
- Volume estimé : ~170k lignes pour 1000 stations (toutes périodes confondues)
===============================================================================
*/

DROP MATERIALIZED VIEW IF EXISTS public.mv_records_battus;

CREATE MATERIALIZED VIEW public.mv_records_battus AS

SELECT
    period_type,
    period_value,
    record_type,
    station_code,
    station_name,
    department,
    record_value,
    record_date
FROM public.v_records_battus;

-- ============================================================================
-- INDEX
-- ============================================================================

-- Index principal utilisé par l'endpoint (filtre sur les 3 colonnes de recherche)
CREATE INDEX idx_mv_records_battus_query
ON public.mv_records_battus (record_type, period_type, period_value);

-- Index secondaire pour les requêtes par station (diagnostic, admin)
CREATE INDEX idx_mv_records_battus_station
ON public.mv_records_battus (station_code);
