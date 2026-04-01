# CI Pipeline — `ci.yml`

Pipeline d'intégration continue déclenché à chaque `push` sur n'importe quelle branche.

---

## Jobs

### 1. `basic-pipeline`

Vérifie la qualité du code backend et frontend.

**Étapes :**

| Étape | Description |
|---|---|
| Checkout | Clone le dépôt avec historique complet (`fetch-depth: 0`) |
| Setup uv / Python 3.13 | Installe l'environnement Python via `uv` |
| Setup Node 24 | Installe Node.js avec cache npm |
| Install backend deps | `uv sync` + démarrage de TimescaleDB via Docker Compose |
| Install frontend deps | `npm ci` + ajout de vitest |
| Tests backend | `pytest` avec export JUnit XML uploadé en artifact |
| Lint backend | `ruff check` (règle DJ001 ignorée) |
| Lint frontend | `npm run lint` |
| Scan Trivy | Analyse du filesystem pour vulnérabilités HIGH/CRITICAL |
| Upload rapport Trivy | Rapport uploadé en artifact même en cas d'échec |
| Check Trivy | Fait échouer le job si des vulnérabilités sont détectées |

---

### 2. `docker-build-push`

Construit et publie les images Docker sur GitHub Container Registry (GHCR).
Déclenché uniquement si `basic-pipeline` réussit.

**Images produites :**

| Service | Image |
|---|---|
| Backend | `ghcr.io/<owner>/<repo>/backend` |
| Frontend | `ghcr.io/<owner>/<repo>/frontend` |

**Tags appliqués :** `latest` + SHA court du commit.

**Note :** l'authentification utilise le secret `CR_PAT` (Personal Access Token)
au lieu du `GITHUB_TOKEN` par défaut, nécessaire car le dépôt est un fork
(le token par défaut y est restreint en écriture sur GHCR).

---

## Secrets requis

| Secret | Usage |
|---|---|
| `CR_PAT` | Token GitHub avec scope `write:packages` pour pousser sur GHCR |

## Artifacts produits

| Artifact | Contenu |
|---|---|
| `test-report` | Résultats pytest au format JUnit XML |
| `security-report` | Rapport Trivy des vulnérabilités détectées |
