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

# 4. Retourner dans le dossier backend/scripts et générer les données mock
cd ../scripts
bash seed_dev.sh
# 6. Vérifier via l'API
uv run python manage.py runserver
# Puis ouvrir http://localhost:8000/api/stations/
```

## Données disponibles

L'environnement de dev contient :
- toutes les stations
- toutes les données quotidiennes pour 2024-2025

## Exemples de requêtes

```bash
#Liste des stations :
curl -L http://localhost:8000/api/v1/stations/
curl -L http://localhost:8000/api/v1/stations?departement=13

#Indicateur thermique national :
curl "http://localhost:8000/api/v1/temperature/national-indicator?date_start=2025-01-01&date_end=2025-01-31&granularity=month"
```
#
## Architecture : Django + TimescaleDB

La base de développement n'est pas générée par Django (managed=False)

Elle est alimentée par :

- un schéma SQL
- un dump des stations (non commité)
- un export CSV des données quotidiennes (non commité)
- des vues SQL utilisées par Django

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

## Dépannage

### Le container ne démarre pas

```bash
docker-compose logs
docker-compose down -v
docker-compose up -d
```

### La base est vide

```bash
cd backend/scripts
bash seed_dev.sh
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
