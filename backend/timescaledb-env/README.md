# Environnement TimescaleDB pour InfoClimat

Environnement Docker minimal avec TimescaleDB pour développement local.
Le schéma et les données sont gérés par Django.

## Prérequis

1. **Docker** et **Docker Compose** installés
2. **uv** (gestionnaire de paquets Python moderne)

### Installation de uv

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ou via pip
pip install uv
```

## Démarrage rapide

```bash
# 1. Se placer dans le dossier timescaledb-env
cd backend/timescaledb-env

# 2. Démarrer TimescaleDB
docker-compose up -d

# 3. Attendre que le container soit prêt
docker-compose logs -f

# 4. Retourner dans le dossier backend et appliquer les migrations Django
cd ..
uv run python manage.py migrate

# 5. Générer les données mock
uv run python manage.py populate_weather_data

# 6. Vérifier via l'API
uv run python manage.py runserver
# Puis ouvrir http://localhost:8000/api/stations/
```

## Données disponibles

L'environnement contient **15 stations météo françaises** avec **30 jours de données** :

### Stations incluses

- Paris-Montsouris
- Lyon-Bron
- Marseille-Marignane
- Bordeaux-Mérignac
- Lille-Lesquin
- Toulouse-Blagnac
- Nantes-Bouguenais
- Strasbourg-Entzheim
- Brest-Guipavas
- Nice-Côte d'Azur
- Chamonix (montagne)
- Montpellier-Fréjorgues
- Rennes-Saint-Jacques
- Dijon-Longvic
- Pau-Uzein

### Tables disponibles

#### 1. `weather_station`
Métadonnées des stations météo (15 stations)

**Colonnes principales :**
- `id` : Clé primaire auto-générée
- `code` : Identifiant unique (8 caractères)
- `nom` : Nom de la station
- `lat`, `lon`, `alt` : Coordonnées GPS et altitude
- `departement` : Numéro de département
- `poste_ouvert` : Station active (boolean)
- `poste_public` : Données publiques (boolean)

#### 2. `weather_horairetempsreel`
Données horaires en temps réel (~10 800 enregistrements) - **Hypertable TimescaleDB**

**Colonnes principales :**
- `station_id` : Clé étrangère vers Station
- `validity_time` : Timestamp de la mesure
- `t`, `td`, `tx`, `tn` : Températures (°C)
- `u`, `ux`, `un` : Humidité relative (%)
- `dd`, `ff` : Direction et force du vent (°, m/s)
- `fxy`, `fxi` : Rafales de vent (m/s)
- `rr1` : Précipitations horaires (mm)
- `pres`, `pmer` : Pression atmosphérique (hPa)
- `vv` : Visibilité (m)
- `n` : Nébulosité (0-8)
- `t_10`, `t_20`, `t_50`, `t_100` : Températures du sol (°C)

#### 3. `weather_quotidienne`
Données journalières agrégées (~450 enregistrements) - **Hypertable TimescaleDB**

**Colonnes principales :**
- `station_id` : Clé étrangère vers Station
- `date` : Date
- `rr` : Cumul de précipitations (mm)
- `tn`, `tx`, `tm` : Températures min, max, moyenne (°C)
- `tampli` : Amplitude thermique (°C)
- `htn`, `htx` : Heures des extrema (HHMM)
- `ffm` : Vitesse moyenne du vent (m/s)
- `fxy`, `dxy` : Rafale maximale et direction
- `q*` : Flags de qualité (1 = valide)

## Commande Django de peuplement

```bash
# Générer toutes les données (30 jours par défaut)
python manage.py populate_weather_data

# Générer seulement 7 jours de données
python manage.py populate_weather_data --days 7

# Vider les données avant de régénérer
python manage.py populate_weather_data --clear

# Générer uniquement les stations
python manage.py populate_weather_data --stations-only

# Ne pas générer les agrégations quotidiennes
python manage.py populate_weather_data --skip-daily

# Utiliser un seed différent
python manage.py populate_weather_data --seed 123
```

## Exemples de requêtes

### Lister les stations

```sql
SELECT id, code, nom, lat, lon, alt, departement
FROM weather_station
ORDER BY nom;
```

### Dernières mesures d'une station (Paris)

```sql
SELECT
    validity_time,
    t as temperature,
    u as humidite,
    ff as vent_vitesse,
    dd as vent_direction,
    rr1 as pluie
FROM weather_horairetempsreel h
JOIN weather_station s ON h.station_id = s.id
WHERE s.code = '75114001'
ORDER BY validity_time DESC
LIMIT 24;
```

### Agrégation temporelle avec TimescaleDB `time_bucket`

```sql
SELECT
    time_bucket('6 hours', validity_time) as periode,
    s.code,
    AVG(h.t) as temp_moyenne,
    MAX(h.t) as temp_max,
    MIN(h.t) as temp_min
FROM weather_horairetempsreel h
JOIN weather_station s ON h.station_id = s.id
WHERE s.code = '75114001'
GROUP BY periode, s.code
ORDER BY periode DESC;
```

## Architecture : Django + TimescaleDB

### Gestion du schéma par Django

Le schéma de base de données est **entièrement géré par Django** via les migrations :

1. **`0001_initial.py`** : Crée les tables via l'ORM Django (Station, HoraireTempsReel, Quotidienne)
2. **`0002_timescaledb_hypertables.py`** : Migration custom avec `RunSQL` qui :
   - Crée l'extension TimescaleDB
   - Convertit les tables en hypertables
   - Crée des clés primaires composites (id + colonne de temps)
   - Ajoute des index optimisés

**Note importante** : TimescaleDB exige que toute contrainte unique inclue la colonne de partitionnement. Django génère un `id` BigAutoField comme clé primaire, mais les migrations le remplacent par une clé composite `(id, validity_time)` ou `(id, date)`.

### Hypertables configurées

Les tables `weather_horairetempsreel` et `weather_quotidienne` sont configurées comme **hypertables** :

```sql
-- Voir les hypertables
SELECT * FROM timescaledb_information.hypertables;

-- Voir les chunks (partitions temporelles)
SELECT * FROM timescaledb_information.chunks;
```

**Avantages :**
- Requêtes temporelles optimisées
- Partitionnement automatique par période
- Compression possible des anciennes données

## Gestion du container

### Commandes utiles

```bash
# Voir les logs
docker-compose logs -f

# Arrêter l'environnement
docker-compose down

# Arrêter ET supprimer les données
docker-compose down -v

# Se connecter en psql
docker exec -it infoclimat-timescaledb psql -U infoclimat -d meteodb

# Sauvegarder la base
docker exec infoclimat-timescaledb pg_dump -U infoclimat meteodb > backup.sql
```

### Connexion depuis un outil GUI

**DBeaver / pgAdmin / TablePlus :**
- Host : `localhost`
- Port : `5432`
- Database : `meteodb`
- User : `infoclimat`
- Password : `infoclimat2026`

## Unités

- **Températures** : °C
- **Vent** : m/s et degrés (0° = Nord, 90° = Est, 180° = Sud, 270° = Ouest)
- **Précipitations** : mm
- **Pression** : hPa
- **Humidité** : %
- **Visibilité** : mètres
- **Nébulosité** : 0 (ciel clair) à 8 (ciel couvert)

## Dépannage

### Le container ne démarre pas

```bash
docker-compose logs
docker-compose down -v
docker-compose up -d
```

### La base est vide

```bash
cd backend
uv run python manage.py migrate
uv run python manage.py populate_weather_data
```

### Port 5432 déjà utilisé

Modifier dans `docker-compose.yml` :
```yaml
ports:
  - "5433:5432"
```

Et dans `backend/.env` :
```
DB_PORT=5433
```

## Ressources

- [Documentation TimescaleDB](https://docs.timescale.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Django Documentation](https://docs.djangoproject.com/)

---

**Bon développement ! **
