# Environnement TimescaleDB pour InfoClimat

Environnement Docker minimal avec TimescaleDB et données météo mock pour développement local.

## 📋 Prérequis

1. **Docker** et **Docker Compose** installés
2. **uv** (gestionnaire de paquets Python moderne)

### Installation de uv

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ou via pip
pip install uv
```

## 🚀 Démarrage rapide

```bash
# 1. Se placer dans le dossier
cd timescaledb-env

# 2. Démarrer TimescaleDB
docker-compose up -d

# 3. Attendre que le container soit prêt (quelques secondes)
docker-compose logs -f

# 4. Générer et charger les données mock
uv run docker/generate-mock-data.py

# 5. Se connecter à la base de données
docker exec -it infoclimat-timescaledb psql -U infoclimat -d meteodb
```

## 📊 Données disponibles

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

#### 1. `Station`
Métadonnées des stations météo (15 stations)

**Colonnes principales :**
- `id` : Identifiant unique (8 caractères)
- `nom` : Nom de la station
- `lat`, `lon`, `alt` : Coordonnées GPS et altitude
- `departement` : Numéro de département
- `posteOuvert` : Station active (boolean)
- `postePublic` : Données publiques (boolean)

#### 2. `HoraireTempsReel`
Données horaires en temps réel (~10 800 enregistrements)

**Colonnes principales :**
- `geo_id_insee` : ID de la station
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

#### 3. `Quotidienne`
Données journalières agrégées (~450 enregistrements)

**Colonnes principales :**
- `NUM_POSTE` : ID de la station
- `AAAAMMJJ` : Date
- `RR` : Cumul de précipitations (mm)
- `TN`, `TX`, `TM` : Températures min, max, moyenne (°C)
- `TAMPLI` : Amplitude thermique (°C)
- `HTN`, `HTX` : Heures des extrema (HHMM)
- `FFM` : Vitesse moyenne du vent (m/s)
- `FXY`, `DXY` : Rafale maximale et direction
- `Q*` : Flags de qualité (1 = valide)

## 🔍 Exemples de requêtes

### Lister les stations

```sql
SELECT id, nom, lat, lon, alt, departement
FROM "Station"
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
FROM "HoraireTempsReel"
WHERE geo_id_insee = '75114001'
ORDER BY validity_time DESC
LIMIT 24;
```

### Moyenne quotidienne des températures

```sql
SELECT
    "AAAAMMJJ" as date,
    "NUM_POSTE",
    "TN" as temp_min,
    "TX" as temp_max,
    "TM" as temp_moyenne,
    "RR" as pluie_mm
FROM "Quotidienne"
WHERE "NUM_POSTE" = '75114001'
ORDER BY "AAAAMMJJ" DESC
LIMIT 30;
```

### Stations les plus proches d'un point GPS

```sql
-- Paris : 48.8566° N, 2.3522° E
SELECT
    id,
    nom,
    lat,
    lon,
    SQRT(POWER(lat - 48.8566, 2) + POWER(lon - 2.3522, 2)) as distance
FROM "Station"
ORDER BY distance
LIMIT 5;
```

### Agrégation temporelle avec TimescaleDB `time_bucket`

```sql
-- Moyenne horaire des températures sur 6 heures
SELECT
    time_bucket('6 hours', validity_time) as periode,
    geo_id_insee,
    AVG(t) as temp_moyenne,
    MAX(t) as temp_max,
    MIN(t) as temp_min
FROM "HoraireTempsReel"
WHERE geo_id_insee = '75114001'
GROUP BY periode, geo_id_insee
ORDER BY periode DESC;
```

### Comparaison entre stations

```sql
SELECT
    s.nom as station,
    AVG(h.t) as temp_moyenne,
    AVG(h.u) as humidite_moyenne,
    SUM(h.rr1) as pluie_totale
FROM "HoraireTempsReel" h
JOIN "Station" s ON h.geo_id_insee = s.id
WHERE h.validity_time >= NOW() - INTERVAL '7 days'
GROUP BY s.nom
ORDER BY temp_moyenne DESC;
```

### Extrêmes météorologiques

```sql
-- Températures extrêmes du mois
SELECT
    s.nom,
    "TX" as temp_max,
    "HTX" as heure_max,
    "TN" as temp_min,
    "HTN" as heure_min,
    "AAAAMMJJ" as date
FROM "Quotidienne" q
JOIN "Station" s ON q."NUM_POSTE" = s.id
WHERE "TX" = (SELECT MAX("TX") FROM "Quotidienne")
   OR "TN" = (SELECT MIN("TN") FROM "Quotidienne");
```

## 🛠️ TimescaleDB : Fonctionnalités avancées

### Hypertables configurées

Les tables `HoraireTempsReel` et `Quotidienne` sont configurées comme **hypertables** :

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

### Compression des données (optionnel)

```sql
-- Activer la compression sur une hypertable
ALTER TABLE "HoraireTempsReel" SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'geo_id_insee'
);

-- Ajouter une politique de compression (données > 7 jours)
SELECT add_compression_policy(
    '"HoraireTempsReel"',
    INTERVAL '7 days'
);
```

### Politique de rétention (optionnel)

```sql
-- Supprimer automatiquement les données > 1 an
SELECT add_retention_policy(
    '"HoraireTempsReel"',
    INTERVAL '1 year'
);
```

### Requêtes continues (Continuous Aggregates)

```sql
-- Créer une agrégation continue pour moyennes journalières
CREATE MATERIALIZED VIEW daily_weather_summary
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', validity_time) AS day,
    geo_id_insee,
    AVG(t) as avg_temp,
    AVG(u) as avg_humidity,
    SUM(rr1) as total_rain
FROM "HoraireTempsReel"
GROUP BY day, geo_id_insee;

-- Rafraîchir automatiquement
SELECT add_continuous_aggregate_policy(
    'daily_weather_summary',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);
```

## 🔧 Gestion du container

### Commandes utiles

```bash
# Voir les logs
docker-compose logs -f

# Arrêter l'environnement
docker-compose down

# Arrêter ET supprimer les données
docker-compose down -v

# Redémarrer
docker-compose restart

# Se connecter en psql
docker exec -it infoclimat-timescaledb psql -U infoclimat -d meteodb

# Sauvegarder la base
docker exec infoclimat-timescaledb pg_dump -U infoclimat meteodb > backup.sql

# Restaurer une sauvegarde
docker exec -i infoclimat-timescaledb psql -U infoclimat -d meteodb < backup.sql
```

### Connexion depuis Python

```python
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='meteodb',
    user='infoclimat',
    password='infoclimat2026'
)

cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM "Station"')
print(f"Nombre de stations: {cursor.fetchone()[0]}")
conn.close()
```

### Connexion depuis un outil GUI

**DBeaver / pgAdmin / TablePlus :**
- Host : `localhost`
- Port : `5432`
- Database : `meteodb`
- User : `infoclimat`
- Password : `infoclimat2026`

## 📖 Documentation des données

### Codes de qualité (Q-prefix)

Les colonnes `Q*` dans la table `Quotidienne` indiquent la qualité :
- `1` : Donnée valide
- `0` : Donnée manquante
- Autres valeurs : Codes spécifiques (voir documentation Météo-France)

### Format des heures (H-prefix)

Les colonnes `HTN`, `HTX`, `HXY` sont au format `HHMM` (ex: `1430` = 14h30)

### Unités

- **Températures** : °C
- **Vent** : m/s et degrés (0° = Nord, 90° = Est, 180° = Sud, 270° = Ouest)
- **Précipitations** : mm
- **Pression** : hPa
- **Humidité** : %
- **Visibilité** : mètres
- **Nébulosité** : 0 (ciel clair) à 8 (ciel couvert)

## 🐛 Dépannage

### Le container ne démarre pas

```bash
# Vérifier les logs
docker-compose logs

# Supprimer le volume et recréer
docker-compose down -v
docker-compose up -d
```

### Erreur de connexion Python

```bash
# Vérifier que uv utilise les bonnes dépendances
uv pip list

# Réinstaller
uv sync
```

### La base est vide

```bash
# Régénérer les données
uv run docker/generate-mock-data.py
```

### Port 5432 déjà utilisé

Modifier dans `docker-compose.yml` :
```yaml
ports:
  - "5433:5432"  # Utiliser le port 5433 à la place
```

Et dans `docker/generate-mock-data.py` :
```python
DB_PARAMS = {
    'port': 5433,  # Modifier ici aussi
    ...
}
```

## 📚 Ressources

- [Documentation TimescaleDB](https://docs.timescale.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [InfoClimat API](https://www.infoclimat.fr/opendata/)
- [Météo-France Données Publiques](https://donneespubliques.meteofrance.fr/)

## 🤝 Contribution

Cet environnement est conçu pour faciliter le développement local. N'hésitez pas à :
- Ajouter d'autres stations dans `generate-mock-data.py`
- Créer des vues SQL utiles
- Améliorer les données mock pour plus de réalisme
- Partager vos requêtes SQL intéressantes

## 📝 Notes techniques

### Caractéristiques des données mock

- **Reproductibilité** : Seed random fixe (42) pour générer toujours les mêmes données
- **Réalisme** :
  - Cycles diurnes de température (min à 6h, max à 15h)
  - Corrélations météo (pluie → baisse température → hausse humidité)
  - Variations géographiques (altitude, latitude)
  - Tendances baromètriques progressives
- **Performance** : Insertion par batch de 1000 lignes
- **Format** : Timestamps UTC en timestamp(3) (précision milliseconde)

### TimescaleDB vs PostgreSQL classique

**Hypertables** = Tables partitionnées automatiquement par temps
- **Chunking** : Données découpées en morceaux (7 jours pour horaire, 30 jours pour quotidien)
- **Compression** : Réduction de 90%+ du stockage possible
- **Requêtes** : Optimisées pour les plages temporelles
- **Rétention** : Suppression automatique des anciennes données

**Compatibilité** : 100% compatible PostgreSQL (requêtes SQL standards)

## ⚙️ Configuration

### Variables d'environnement

Modifiables dans `docker-compose.yml` :

```yaml
environment:
  POSTGRES_USER: infoclimat      # Utilisateur PostgreSQL
  POSTGRES_PASSWORD: infoclimat2026  # Mot de passe
  POSTGRES_DB: meteodb           # Nom de la base
```

### Volumes

- `timescaledb-data` : Données PostgreSQL persistantes
- `./docker` : Scripts d'initialisation (lecture seule)

## 🎯 Cas d'usage

Cet environnement est parfait pour :
- ✅ Développer des applications météo
- ✅ Tester des requêtes SQL complexes
- ✅ Apprendre TimescaleDB
- ✅ Prototyper des visualisations de données
- ✅ Former des bénévoles aux données InfoClimat
- ❌ Production (utiliser les vraies données et une configuration sécurisée)

---

**Bon développement ! 🌦️**
