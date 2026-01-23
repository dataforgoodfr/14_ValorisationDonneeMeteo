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
# Appliquer les migrations Django
uv run python manage.py migrate

# Demarrer le serveur de developpement
uv run python manage.py runserver
```

L'API est disponible sur http://localhost:8000

## Endpoints API

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

### Linting

```bash
uv run ruff check .
uv run ruff format .
```

## Structure du projet

```
backend/
├── config/             # Configuration Django
│   ├── settings.py     # Settings (django-environ)
│   ├── urls.py         # Routes principales
│   └── wsgi.py
├── weather/            # App principale
│   ├── models.py       # Models (Station, HoraireTempsReel, Quotidienne)
│   ├── serializers.py  # Serializers DRF
│   ├── views.py        # ViewSets
│   ├── filters.py      # Filtres API
│   └── urls.py         # Routes API v1
├── timescaledb-env/    # Environnement TimescaleDB
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
