# Backend - API Meteo

API REST Django/DRF pour les donnees meteorologiques InfoClimat.

## Prerequis

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) pour la gestion des dependances
- Docker (pour TimescaleDB)

## Installation

```bash
cd backend

# Installer les dependances, ainsi que les dépendances optionnelles de dev
uv sync --extra dev

# Copier la configuration
cp .env.example .env
```

## Demarrer TimescaleDB

```bash
cd timescaledb-env
docker compose up -d
cd ..
```
## Initialiser la base de développement

Contrairement aux premières versions du projet, la base de développement n'est pas générée par Django.

Elle est alimentée par :

- un schéma SQL

- un dump des stations

- un export CSV des données quotidiennes

- des vues SQL utilisées par Django

Initialisation :
```
cd backend/scripts
bash seed_dev.sh
```
Ce script :

- recrée le schéma public
- crée les tables sources (Station, Quotidienne)
- importe les données :
  - stations
  - données quotidiennes
  - applique les vues SQL utilisées par l'API

## Lancer le serveur

```bash
# Appliquer les migrations Django (cree les tables + hypertables TimescaleDB)
uv run python manage.py migrate

# Peupler la base avec des donnees de test
uv run python manage.py populate_weather_data

# Demarrer le serveur de developpement
uv run python manage.py runserver
```

L'API est disponible sur http://localhost:8000

## Architecture des données

Le backend ne manipule pas directement les tables sources via l'ORM Django.

Les modèles Django sont basés sur des views SQL.
```
Station (table source)
Quotidienne (table source)

      ↓
v_station
v_quotidienne_itn

      ↓

models Django

      ↓

Data sources (Python)

      ↓

Services métier

      ↓

API REST
```
Cela permet :

- de stabiliser l'API
- d'éviter les dépendances directes au schéma source

## API

### Spécifications

Les spécifications de l'API (la cible a atteindre) sont disponibles dans `openapi/target-specs/openapi.yaml`

```
cd backend

npx swagger-ui-watcher openapi/target-specs/openapi.yaml
```

La documentation est alors disponible sur `http://localhost:8000`

| Endpoint                  | Description                   |
|---------------------------|-------------------------------|
| `/api/v1/stations/`       | Liste des stations meteo      |
| `/api/v1/temperature/national-indicator`    | Indicateur thermique national


## Exemples de requetes

```bash
#Liste des stations :

curl http://localhost:8000/api/v1/stations/

#Indicateur thermique national :

curl "http://localhost:8000/api/v1/temperature/national-indicator?date_start=2025-01-01&date_end=2025-01-31&granularity=month"
```

## Developpement

### Pre-commit hooks

*L'installation des hooks est décrite dans le [README.md](../README.md) à la racine*

Pour exécuter les hooks backend uniquement :

```bash
# Avec uv (recommandé)
cd backend
uv run pre-commit run --all-files --config=.pre-commit-config.yaml
```

### Tests

```bash
uv run pytest
```

### Factories (Factory Boy)

Des factories sont disponibles pour creer des donnees de test :

```python
from weather.factories import StationFactory, HoraireTempsReelFactory, QuotidienneFactory

# Creer une station
station = StationFactory()

# Creer une mesure horaire pour une station
mesure = HoraireTempsReelFactory(station=station)

# Creer une mesure quotidienne
quotidienne = QuotidienneFactory(station=station)
```

### Linting

```bash
uv run ruff check .
uv run ruff format .
```


## Configuration

Les variables d'environnement sont definies dans `.env` :

| Variable               | Description        | Defaut                  |
|------------------------|--------------------|-------------------------|
| `DEBUG`                | Mode debug         | `true`                  |
| `SECRET_KEY`           | Cle secrete Django | -                       |
| `DB_HOST`              | Hote PostgreSQL    | `localhost`             |
| `DB_PORT`              | Port PostgreSQL    | `5432`                  |
| `DB_NAME`              | Nom de la base     | `meteodb`               |
| `DB_USER`              | Utilisateur        | `infoclimat`            |
| `DB_PASSWORD`          | Mot de passe       | `infoclimat2026`        |
| `CORS_ALLOWED_ORIGINS` | Origins CORS       | `http://localhost:5173` |


### Connexion directe a la base de dev

```bash
docker exec -it infoclimat-timescaledb psql -U infoclimat -d meteodb

-- Voir les hypertables
SELECT * FROM timescaledb_information.hypertables;

-- Voir les chunks (partitions)
SELECT * FROM timescaledb_information.chunks;
```

## Notebooks

###ITN
Un notebook est disponible pour visualiser les données générées par le service national-indicator (fake datasource + agrégation).

1️⃣ Installer les dépendances notebook

Les dépendances notebook ne sont pas installées par défaut.

Depuis le dossier backend/ :

```
uv sync --extra notebook
```

2️⃣ Lancer Jupyter

Toujours depuis backend/ :

```
uv run jupyter lab
```

Puis ouvrir le notebook situé dans `weather/notebooks/`
