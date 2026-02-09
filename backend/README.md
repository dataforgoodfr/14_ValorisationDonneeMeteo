# Backend - API Meteo

API REST Django/DRF pour les donnees meteorologiques InfoClimat.

## Prerequis

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) pour la gestion des dependances
- Docker (pour TimescaleDB)

## Installation

```bash
cd backend

# Installer les dependances
uv sync

# Copier la configuration
cp .env.example .env
```

## Demarrer TimescaleDB

```bash
cd timescaledb-env
docker compose up -d
cd ..
```

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

## Commandes de gestion

### populate_weather_data

Genere des donnees meteo realistes pour le developpement et les tests.

> **Note** : Cette commande necessite `DEBUG=True` dans les settings. Elle refuse de s'executer en production pour eviter toute suppression accidentelle de donnees.

```bash
# Generer 30 jours de donnees (defaut)
uv run python manage.py populate_weather_data

# Generer 7 jours de donnees
uv run python manage.py populate_weather_data --days 7

# Vider les donnees existantes avant de regenerer
uv run python manage.py populate_weather_data --clear

# Generer uniquement les stations (sans donnees meteo)
uv run python manage.py populate_weather_data --stations-only

# Ne pas generer les agregations quotidiennes
uv run python manage.py populate_weather_data --skip-daily

# Utiliser un seed specifique pour la reproductibilite
uv run python manage.py populate_weather_data --seed 123
```

Les donnees generees incluent 15 stations francaises avec des mesures realistes :
- Cycles de temperature diurnes (min a 6h, max a 14h)
- Humidite inversement correlee a la temperature
- Variations de pression atmospherique coherentes
- Rafales de vent avec direction aleatoire

## API
### Spécifications
Les spécifications de l'API (la cible a atteindre) sont disponibles dans `openapi/target-specs/openapi.yaml`
```
cd backend
```
```
npx swagger-ui-watcher openapi/target-specs/openapi.yaml
```
La documentation est alors disponible sur `http://localhost:8000`
Ce document est mis à jour au cours de la vie du projet

### Endpoints existants
| Endpoint | Description |
|----------|-------------|
| `/api/v1/stations/` | Liste des stations meteo |
| `/api/v1/horaire/` | Mesures horaires temps reel |
| `/api/v1/horaire/latest/` | Derniere mesure par station |
| `/api/v1/quotidien/` | Donnees journalieres agregees |
| `/api/docs/` | Documentation Swagger UI |
| `/api/redoc/` | Documentation ReDoc |
| `/api/schema/` | Schema OpenAPI |

## Exemples de requetes

```bash
# Liste des stations
curl http://localhost:8000/api/v1/stations/

# Filtrer par departement
curl "http://localhost:8000/api/v1/stations/?departement=75"

# Mesures horaires avec filtre de date
curl "http://localhost:8000/api/v1/horaire/?validity_time_after=2026-01-15"

# Derniere mesure de chaque station
curl http://localhost:8000/api/v1/horaire/latest/
```

## Developpement

### Pre-commit hooks

```bash
uv run pre-commit install
uv run pre-commit run --all-files
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

## Structure du projet

```
backend/
├── config/                     # Configuration Django
│   ├── settings.py             # Settings (django-environ)
│   ├── urls.py                 # Routes principales
│   └── wsgi.py
├── weather/                    # App principale
│   ├── models.py               # Models (Station, HoraireTempsReel, Quotidienne)
│   ├── serializers.py          # Serializers DRF
│   ├── views.py                # ViewSets
│   ├── filters.py              # Filtres API
│   ├── urls.py                 # Routes API v1
│   ├── admin.py                # Interface admin Django
│   ├── migrations/             # Migrations Django + TimescaleDB hypertables
│   ├── management/
│   │   └── commands/
│   │       └── populate_weather_data.py  # Commande de peuplement
│   ├── data_generators/        # Generateurs de donnees realistes
│   │   ├── constants.py        # Stations et parametres
│   │   └── weather_physics.py  # Algorithmes de generation meteo
│   ├── factories/              # Factories Factory Boy (pour les tests)
│   │   └── weather.py
│   └── tests/
├── timescaledb-env/            # Environnement Docker TimescaleDB
├── manage.py
├── pyproject.toml
└── .env.example
```

## Configuration

Les variables d'environnement sont definies dans `.env` :

| Variable | Description | Defaut |
|----------|-------------|--------|
| `DEBUG` | Mode debug | `true` |
| `SECRET_KEY` | Cle secrete Django | - |
| `DB_HOST` | Hote PostgreSQL | `localhost` |
| `DB_PORT` | Port PostgreSQL | `5432` |
| `DB_NAME` | Nom de la base | `meteodb` |
| `DB_USER` | Utilisateur | `infoclimat` |
| `DB_PASSWORD` | Mot de passe | `infoclimat2026` |
| `CORS_ALLOWED_ORIGINS` | Origins CORS | `http://localhost:5173` |

## TimescaleDB

Le backend utilise TimescaleDB pour optimiser les requetes sur les donnees temporelles.

### Hypertables

Les tables `weather_horairetempsreel` et `weather_quotidienne` sont configurees comme **hypertables** :
- Partitionnement automatique par intervalles de temps
- Requetes temporelles optimisees
- Compression possible des anciennes donnees

### Migrations Django

Le schema est entierement gere par Django :
1. `0001_initial.py` : Creation des tables via l'ORM Django
2. `0002_timescaledb_hypertables.py` : Conversion en hypertables via `RunSQL`

**Note** : Les hypertables TimescaleDB necessitent que les colonnes de partitionnement (`validity_time`, `date`) soient incluses dans les cles primaires. Les migrations gerent cela automatiquement.

### Connexion directe a la base

```bash
docker exec -it infoclimat-timescaledb psql -U infoclimat -d meteodb

-- Voir les hypertables
SELECT * FROM timescaledb_information.hypertables;

-- Voir les chunks (partitions)
SELECT * FROM timescaledb_information.chunks;
```
