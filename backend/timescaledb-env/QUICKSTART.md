# 🚀 Guide de démarrage rapide (5 minutes)

Pour les bénévoles qui veulent un environnement prêt à l'emploi **maintenant**.

## Prérequis (à installer une seule fois)

1. **Docker Desktop** : https://www.docker.com/products/docker-desktop
2. **uv** : `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Installation (3 commandes)

```bash
# 1. Démarrer la base de données
cd timescaledb-env
docker-compose up -d

# 2. Attendre 10 secondes que la base soit prête
sleep 10

# 3. Générer les données
uv run docker/generate-mock-data.py
```

✅ **C'est tout !** Vous avez maintenant une base TimescaleDB avec 15 stations et 30 jours de données météo.

## Vérification (1 commande)

```bash
docker exec -it infoclimat-timescaledb psql -U infoclimat -d meteodb -c "SELECT COUNT(*) FROM \"Station\""
```

Devrait afficher : **15**

## Première requête

```bash
docker exec -it infoclimat-timescaledb psql -U infoclimat -d meteodb
```

Puis dans psql :

```sql
-- Voir les stations
SELECT id, nom, lat, lon FROM "Station" LIMIT 5;

-- Dernières mesures de Paris
SELECT validity_time, t, u, ff, rr1
FROM "HoraireTempsReel"
WHERE geo_id_insee = '75114001'
ORDER BY validity_time DESC
LIMIT 10;

-- Quitter
\q
```

## Connexion depuis Python

Créez `test.py` :

```python
import psycopg2

conn = psycopg2.connect(
    host='localhost', port=5432,
    database='meteodb', user='infoclimat', password='infoclimat2026'
)
cursor = conn.cursor()

cursor.execute('SELECT nom, lat, lon FROM "Station" LIMIT 5')
for row in cursor.fetchall():
    print(f"Station: {row[0]} ({row[1]:.2f}, {row[2]:.2f})")

conn.close()
```

Puis : `uv run test.py`

## Arrêter l'environnement

```bash
docker-compose down        # Arrêter (données conservées)
docker-compose down -v     # Arrêter et supprimer les données
```

## En cas de problème

### "Port 5432 already in use"

```bash
# Dans docker-compose.yml, changer:
ports:
  - "5433:5432"  # Au lieu de 5432:5432

# Puis dans docker/generate-mock-data.py, ligne 17:
'port': 5433,  # Au lieu de 5432
```

### "Connection refused"

```bash
# Attendre un peu plus
sleep 20

# Vérifier que le container tourne
docker ps | grep timescaledb

# Voir les logs
docker-compose logs
```

### Base vide

```bash
# Régénérer les données
uv run docker/generate-mock-data.py
```

## 📚 Suite

Pour aller plus loin, voir :
- [README.md](README.md) - Documentation complète
- [STRUCTURE.md](STRUCTURE.md) - Architecture du projet

## 💡 Astuces

**GUI Database** : Installez [DBeaver](https://dbeaver.io/) pour explorer visuellement
- Host: `localhost`, Port: `5432`
- Database: `meteodb`, User: `infoclimat`, Password: `infoclimat2026`

**Jupyter Notebook** :
```bash
uv add jupyter
uv run jupyter notebook
```

Puis dans un notebook :
```python
import psycopg2
import pandas as pd

conn = psycopg2.connect(...)
df = pd.read_sql('SELECT * FROM "Station"', conn)
df.head()
```

---

**Besoin d'aide ?** Consultez [README.md](README.md) ou ouvrez une issue.
