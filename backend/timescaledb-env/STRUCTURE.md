# Structure de l'environnement TimescaleDB

## 📁 Arborescence

```
timescaledb-env/
├── docker-compose.yml          # Configuration Docker
├── pyproject.toml              # Dépendances Python (uv)
├── .python-version             # Version Python (3.11)
├── .gitignore                  # Fichiers à ignorer par Git
├── README.md                   # Documentation complète
├── STRUCTURE.md                # Ce fichier
└── docker/
    ├── init-schema.sql         # Schéma des 3 tables + hypertables
    ├── generate-mock-data.py   # Générateur de données mock
    └── load-mock-data.sh       # Script de chargement (Docker)
```

## 📝 Description des fichiers

### Configuration Docker

- **docker-compose.yml** : Container TimescaleDB 2.17.0-pg17
  - Port 5432 exposé
  - Volume persistant `timescaledb-data`
  - Mount `./docker` vers `/docker-entrypoint-initdb.d/`
  - Healthcheck configuré

### Configuration Python

- **pyproject.toml** : Projet uv avec dépendances
  - `psycopg2-binary>=2.9.9` : Driver PostgreSQL
  - `numpy>=1.26.0` : Calculs numériques
- **.python-version** : Python 3.11

### Scripts SQL

- **docker/init-schema.sql** (5.2 KB) : Schéma de base
  - Extension TimescaleDB
  - 3 tables : Station, HoraireTempsReel, Quotidienne
  - 2 hypertables : HoraireTempsReel (7 jours), Quotidienne (30 jours)
  - Index sur colonnes temporelles et géographiques

### Scripts Python

- **docker/generate-mock-data.py** (13.3 KB) : Générateur de données
  - 15 stations françaises (Paris, Lyon, Marseille, etc.)
  - 30 jours de données horaires (~10 800 enregistrements)
  - Données journalières agrégées (~450 enregistrements)
  - Données météo réalistes avec :
    - Cycles diurnes de température
    - Corrélations météo (pluie/température/humidité)
    - Variations géographiques (latitude, altitude)
    - Tendances baromètriques
  - Insertions par batch pour performance

### Scripts Shell

- **docker/load-mock-data.sh** : Script de chargement (container Docker)
  - Vérifie que PostgreSQL est prêt
  - Initialise le schéma SQL
  - Instructions pour exécuter le script Python

## 🎯 Flux d'exécution

1. **Démarrage Docker** : `docker-compose up -d`
   - Démarre TimescaleDB
   - Monte les scripts dans `/docker-entrypoint-initdb.d/`
   - Exécute automatiquement `init-schema.sql`

2. **Génération des données** : `uv run docker/generate-mock-data.py`
   - Se connecte à PostgreSQL (localhost:5432)
   - Insère 15 stations
   - Génère 10 800 mesures horaires
   - Agrège en 450 mesures quotidiennes
   - Affiche un résumé

3. **Utilisation** :
   - Connexion psql : `docker exec -it infoclimat-timescaledb psql -U infoclimat -d meteodb`
   - Connexion Python : voir README.md
   - GUI : DBeaver, pgAdmin, TablePlus

## 📊 Volumétrie

| Élément | Quantité |
|---------|----------|
| Stations | 15 |
| Période | 30 jours |
| Enregistrements horaires | ~10 800 (15 × 24 × 30) |
| Enregistrements quotidiens | ~450 (15 × 30) |
| Chunks TimescaleDB | ~5-6 (7 jours par chunk) |
| Taille base ~| 10-20 MB |

## 🔑 Identifiants par défaut

**ATTENTION : À changer en production !**

- **User** : `infoclimat`
- **Password** : `infoclimat2026`
- **Database** : `meteodb`
- **Port** : `5432`

## ⚡ Performance

- **Insertion** : ~5000-10000 lignes/seconde (batch mode)
- **Requêtes temporelles** : Optimisées par hypertables
- **Mémoire container** : ~200-300 MB
- **Stockage** : ~10-20 MB pour 30 jours de données

## 🛠️ Maintenance

### Régénérer les données

```bash
# Supprimer les données
docker exec -it infoclimat-timescaledb psql -U infoclimat -d meteodb -c 'TRUNCATE "Station", "HoraireTempsReel", "Quotidienne" CASCADE'

# Régénérer
uv run docker/generate-mock-data.py
```

### Reset complet

```bash
docker-compose down -v
docker-compose up -d
uv run docker/generate-mock-data.py
```

### Sauvegarder

```bash
docker exec infoclimat-timescaledb pg_dump -U infoclimat meteodb > backup_$(date +%Y%m%d).sql
```

## 📚 Documentation

Voir [README.md](README.md) pour :
- Guide d'installation détaillé
- Exemples de requêtes SQL
- Documentation TimescaleDB
- Dépannage
- Ressources

---

**Version** : 0.1.0
**Dernière mise à jour** : 2026-01-13
