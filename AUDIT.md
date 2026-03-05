# Audit Système — Plan d'Action

> Audit réalisé le 5 mars 2026 sur le projet ValorisationDonneeMeteo

---

## Résumé

Le projet a de bonnes bases (linting, ORM sécurisé, factories, CI pre-commit) mais présente des lacunes critiques en **monitoring** (inexistant), **sécurité production** (pas de HTTPS, containers root, pas de rate limiting), **tests** (0 tests frontend, pas de CI), et **documentation** (partielle).

---

## 1. Code Quality

### ✅ Ce qui existe

- **Ruff** configuré (lint + format) avec règles E, W, F, I, B, C4, UP, DJ — `backend/pyproject.toml`
- **ESLint + Prettier** frontend — `frontend/eslint.config.mjs`
- **Pre-commit hooks** racine + backend (ruff, ruff-format, nbstripout, check-merge-conflict…)
- **isort** intégré via Ruff (rule I)
- **.editorconfig** (UTF-8, LF, 4 espaces)
- **Lock files** (uv.lock, package-lock.json)
- **CI pre-commit** : `.github/workflows/pre-commit.yaml`

### ❌ Ce qui manque

| Manque                                 | Impact                           | Priorité  |
| -------------------------------------- | -------------------------------- | --------- |
| Type checking Python (mypy/pyright)    | Bugs runtime non détectés        | 🟡 Moyen  |
| Métriques de complexité (McCabe/radon) | Dette technique invisible        | 🟢 Faible |
| Dependabot / audit deps                | Vulnérabilités invisibles        | 🟡 Moyen  |
| Bandit (scanner sécurité Python)       | Failles de sécurité dans le code | 🟡 Moyen  |

### 🔧 Manuel vs Automatisé

| Tâche             | État                                     |
| ----------------- | ---------------------------------------- |
| Linting Python    | ✅ Automatisé (pre-commit + CI)          |
| Formatting Python | ✅ Automatisé (pre-commit + CI)          |
| Linting Frontend  | ✅ Automatisé (pre-commit via npm check) |
| Type checking     | ❌ Manuel (non configuré)                |
| Audit dépendances | ❌ Manuel (pas de Dependabot/safety)     |

### ⚠️ Points de défaillance

- Absence de type checking → bugs runtime non détectés
- Pas de vérification de vulnérabilités dans les dépendances
- Complexité du code non mesurée → dette technique invisible

---

## 2. Testing

### ✅ Ce qui existe

- **7 fichiers de test backend** (5 unit, 2 intégration) — `backend/weather/tests/`
- **pytest + pytest-django + pytest-cov** installés
- **Factories** : StationFactory, HoraireTempsReelFactory, QuotidienneFactory — `backend/weather/factories/`
- **conftest.py** avec fixtures spécialisées (itn_stations, seed_itn_day)
- **Vitest** configuré côté frontend (script `test:unit`)
- **@nuxt/test-utils, @vue/test-utils, @testing-library/vue** installés
- **Playwright** dans les devDependencies

### ❌ Ce qui manque

| Manque                                | Impact                                   | Priorité    |
| ------------------------------------- | ---------------------------------------- | ----------- |
| 0 fichier de test frontend            | Régressions silencieuses                 | 🟠 Élevé    |
| 0 test E2E (Playwright non configuré) | Workflows utilisateur non validés        | 🟡 Moyen    |
| Coverage non configuré                | Pas de visibilité sur la couverture      | 🟠 Élevé    |
| Tests NON exécutés en CI              | Merge de code cassé possible             | 🔴 Critique |
| Tests contrat API (vs openapi.yaml)   | API peut diverger de la spec             | 🟡 Moyen    |
| Tests de charge (k6/Locust)           | Pas de baseline de performance           | 🟢 Faible   |
| Tests modèles Django                  | Station, Horaire, Quotidienne non testés | 🟡 Moyen    |

### 🔧 Manuel vs Automatisé

| Tâche          | État                                         |
| -------------- | -------------------------------------------- |
| Tests backend  | ❌ Manuel (`uv run pytest` local uniquement) |
| Tests frontend | ❌ Inexistants                               |
| Tests E2E      | ❌ Inexistants                               |
| Coverage       | ❌ Non configuré                             |
| Tests en CI    | ❌ Non implémenté                            |

### ⚠️ Points de défaillance

- Régressions frontend silencieuses (0% couverture)
- Merge de code cassé possible (pas de gate CI)
- API peut diverger de la spec OpenAPI sans alerte
- Aucune baseline de performance

---

## 3. Deployment Process

### ✅ Ce qui existe

- **Dockerfiles** backend (python:3.12-slim) et frontend (node:24-alpine, multi-stage)
- **docker-compose.dev.yml** et **docker-compose.test.yml**
- **entrypoint.sh** : migrations + collectstatic + gunicorn
- **CI staging** : build → push GHCR → deploy via Tailscale SSH — `.github/workflows/staging.yml`
- **Nginx** reverse proxy — `nginx/nginx.conf`
- **Health checks Docker** pour TimescaleDB (pg_isready)

### ❌ Ce qui manque

| Manque                              | Impact                   | Priorité    |
| ----------------------------------- | ------------------------ | ----------- |
| docker-compose production dédié     | Pas de config prod       | 🟠 Élevé    |
| Containers tournent en root         | Escalade de privilèges   | 🔴 Critique |
| Backend Dockerfile pas multi-stage  | Image plus lourde        | 🟢 Faible   |
| HTTPS/TLS dans nginx                | Données en clair         | 🔴 Critique |
| Headers sécurité nginx (HSTS, CSP…) | Vulnérabilités web       | 🔴 Critique |
| Rate limiting nginx                 | Vulnérable au DoS        | 🟠 Élevé    |
| Tests avant déploiement             | Images cassées déployées | 🔴 Critique |
| Health check applicatif (/health)   | Redémarrage aveugle      | 🟠 Élevé    |
| Stratégie de rollback               | Pas de retour arrière    | 🟡 Moyen    |

### 🔧 Manuel vs Automatisé

| Tâche               | État                                |
| ------------------- | ----------------------------------- |
| Build images Docker | ✅ Automatisé (CI sur tag)          |
| Push sur GHCR       | ✅ Automatisé                       |
| Déploiement staging | ✅ Semi-auto (CI via Tailscale SSH) |
| Migrations DB       | ✅ Auto (entrypoint.sh)             |
| Tests avant deploy  | ❌ Non implémenté                   |
| Rollback            | ❌ Manuel (pas de stratégie)        |
| Déploiement prod    | ❌ Non défini                       |

### ⚠️ Points de défaillance

- Déploiement d'images cassées (pas de tests gate)
- Containers root → escalade de privilèges possible
- Pas de rollback automatisé
- HTTP uniquement → données en clair
- Pas de health check → redémarrage aveugle

---

## 4. Monitoring — ❌ Quasi-inexistant

### ✅ Ce qui existe

- **Health check Docker** pour TimescaleDB uniquement (pg_isready)
- **prometheus-client** dans uv.lock (dépendance indirecte, non configurée)

### ❌ Ce qui manque — TOUT est absent

| Manque                       | Impact                        | Priorité    |
| ---------------------------- | ----------------------------- | ----------- |
| Configuration LOGGING Django | Pas de logs applicatifs       | 🔴 Critique |
| Logging structuré (JSON)     | Logs inexploitables           | 🔴 Critique |
| Sentry (error tracking)      | Erreurs 500 silencieuses      | 🔴 Critique |
| Prometheus/Grafana           | Pas de métriques              | 🟠 Élevé    |
| Endpoint /health             | Pas de probe applicative      | 🔴 Critique |
| Métriques (latence, erreurs) | Dégradation invisible         | 🟠 Élevé    |
| Slow query logs              | Requêtes lentes non détectées | 🟡 Moyen    |
| Alerting                     | Pas de notification           | 🟠 Élevé    |

### 🔧 Manuel vs Automatisé

| Tâche                     | État                              |
| ------------------------- | --------------------------------- |
| Détection d'erreurs       | ❌ Manuel (lecture de logs bruts) |
| Métriques performance     | ❌ Inexistant                     |
| Alerting                  | ❌ Inexistant                     |
| Health checks applicatifs | ❌ Inexistant                     |

### ⚠️ Points de défaillance

- **Catégorie la plus critique** : impossible de détecter des pannes
- Dégradation de performance invisible
- Erreurs 500 silencieuses en production
- Pas de capacité de diagnostic post-incident

---

## 5. Security

### ✅ Ce qui existe

- **Django ORM** partout (protection SQL injection, pas de raw SQL)
- **CORS restrictif** — `backend/config/settings.py`
- **CSRF middleware** activé
- **XFrameOptions middleware** activé
- **SecurityMiddleware** en première position
- **SECRET_KEY** via variable d'environnement
- **.gitignore** correct (.env exclus, .env.example inclus)
- **API en lecture seule** (ReadOnlyModelViewSet)
- **Validation des entrées** via serializers DRF
- **GitHub Secrets** pour CI (Tailscale, GITHUB_TOKEN)
- **WhiteNoise** pour les fichiers statiques

### ❌ Ce qui manque

| Manque                                                    | Impact                      | Priorité    |
| --------------------------------------------------------- | --------------------------- | ----------- |
| `ALLOWED_HOSTS=*` dans .env.example racine                | Attaque Host header         | 🔴 Critique |
| Mot de passe par défaut `infoclimat2026` dans 5+ fichiers | Accès non autorisé          | 🔴 Critique |
| SECURE_SSL_REDIRECT                                       | Pas de redirection HTTPS    | 🔴 Critique |
| SESSION_COOKIE_SECURE / CSRF_COOKIE_SECURE                | Cookies non sécurisés       | 🔴 Critique |
| HSTS (SECURE_HSTS_SECONDS)                                | Pas de protection downgrade | 🟠 Élevé    |
| Content-Security-Policy                                   | Risque XSS                  | 🟠 Élevé    |
| Rate limiting / throttling                                | Vulnérable au DoS           | 🟠 Élevé    |
| Bandit / pip-audit                                        | Pas de scan sécurité code   | 🟡 Moyen    |
| Containers Docker en root                                 | Escalade de privilèges      | 🔴 Critique |
| Django Admin sans restriction IP                          | Cible brute force           | 🟡 Moyen    |
| CSRF_TRUSTED_ORIGINS pour production                      | CSRF en prod HTTPS          | 🟠 Élevé    |

### 🔧 Manuel vs Automatisé

| Tâche                       | État              |
| --------------------------- | ----------------- |
| Scan de vulnérabilités code | ❌ Non implémenté |
| Scan de dépendances         | ❌ Non implémenté |
| Rotation des secrets        | ❌ Manuel         |
| Audit de sécurité           | ❌ Manuel         |

### ⚠️ Points de défaillance

- `ALLOWED_HOSTS=*` est le risque #1
- Credentials par défaut = accès non autorisé si inchangés en prod
- Pas de HTTPS = interception de données possible
- Pas de rate limiting = vulnérable au DoS
- Admin exposé = cible d'attaque brute force
- Pas de CSP = risque XSS

---

## 6. Documentation

### ✅ Ce qui existe

- **backend/README.md** complet : installation, commandes, structure, API, variables d'env, TimescaleDB
- **Spec OpenAPI** — `backend/openapi/target-specs/openapi.yaml`
- **Swagger UI + ReDoc** auto-générés (`/api/docs/`, `/api/redoc/`)
- **timescaledb-env/README.md**

### ❌ Ce qui manque

| Manque                                         | Impact                      | Priorité  |
| ---------------------------------------------- | --------------------------- | --------- |
| Documentation d'architecture (diagrammes, ADR) | Vision technique absente    | 🟡 Moyen  |
| CONTRIBUTING.md                                | Onboarding difficile        | 🟡 Moyen  |
| CHANGELOG                                      | Pas de traçabilité          | 🟡 Moyen  |
| Doc déploiement production                     | Procédure absente           | 🟠 Élevé  |
| Runbook opérationnel                           | Pas de procédure d'incident | 🟠 Élevé  |
| frontend/README.md détaillé                    | Template Nuxt par défaut    | 🟢 Faible |
| Doc pipeline CI/CD                             | Non documenté               | 🟢 Faible |

### 🔧 Manuel vs Automatisé

| Tâche                   | État            |
| ----------------------- | --------------- |
| Doc API (Swagger/ReDoc) | ✅ Auto-générée |
| Schema OpenAPI          | ✅ Auto-généré  |
| README maintenance      | ❌ Manuel       |
| Changelog               | ❌ Inexistant   |
| Doc architecture        | ❌ Inexistant   |

### ⚠️ Points de défaillance

- Nouveau développeur bloqué sans guide de contribution
- Pas de procédure d'incident documentée
- Frontend sous-documenté
- Pas de traçabilité des changements (changelog)

---

## Top 5 — Analyse détaillée et recommandations

### 🥇 #1 — Monitoring inexistant (Monitoring / Sécurité)

**Constat** : Aucun logging Django configuré, aucun error tracking, aucun endpoint `/health`, aucune métrique. En cas de panne ou d'erreur 500, personne n'est alerté et le diagnostic est impossible.

**Correctif court terme** :

- Ajouter une configuration `LOGGING` dans `settings.py` (console + fichier, niveaux WARNING/ERROR)
- Créer un endpoint `/health/` qui vérifie la connexion DB et retourne un status JSON
- Activer les logs slow queries PostgreSQL dans `docker-compose`

**Solution long terme** :

- Intégrer **Sentry** (error tracking + performance monitoring)
- Déployer **Prometheus** + **Grafana** pour les métriques (latence, taux erreur, requêtes/s)
- Mettre en place un système d'**alerting** (Sentry alerts ou Grafana alerts → Slack/email)
- Configurer du **logging structuré** (JSON) avec `python-json-logger` pour faciliter l'agrégation

**Outils / Technologies** :
| Outil | Rôle | Coût |
|-------|------|------|
| `django-health-check` | Endpoint /health avec checks DB, cache, storage | Gratuit |
| `sentry-sdk[django]` | Error tracking + performance | Gratuit (plan développeur) |
| `python-json-logger` | Logging structuré JSON | Gratuit |
| Prometheus + Grafana | Dashboards métriques | Gratuit (self-hosted) |
| `django-prometheus` | Métriques Django → Prometheus | Gratuit |

---

### 🥈 #2 — Tests non exécutés en CI (Testing / Déploiement)

**Constat** : pytest existe localement mais aucun workflow GitHub Actions n'exécute les tests. Du code cassé peut être mergé et déployé en staging sans détection. Le pipeline staging build les images Docker directement sans étape de validation.

**Correctif court terme** :

- Créer un workflow `.github/workflows/tests.yml` qui exécute `uv run pytest` sur chaque PR et push vers main
- Ajouter une étape de test dans le workflow staging (avant le build Docker)
- Configurer `pytest-cov` avec un seuil minimum (ex: 60%) dans `pyproject.toml`

**Solution long terme** :

- Ajouter un job vitest dans le même workflow CI pour le frontend
- Rendre le merge conditionné par les tests (branch protection rules GitHub)
- Publier les rapports de coverage sur chaque PR (via `coverage-comment` ou Codecov)
- Implémenter une matrice de tests (Python 3.12/3.13, PostgreSQL versions)

**Outils / Technologies** :
| Outil | Rôle | Coût |
|-------|------|------|
| GitHub Actions | CI/CD (déjà en place) | Gratuit (2000 min/mois) |
| `pytest-cov` | Mesure de couverture (déjà installé) | Gratuit |
| `codecov` ou `coveralls` | Rapports de coverage sur PR | Gratuit (open source) |
| Branch protection rules | Gate obligatoire avant merge | Gratuit |
| `act` | Tester les workflows CI localement | Gratuit |

---

### 🥉 #3 — Sécurité production non configurée (Sécurité / Déploiement)

**Constat** : `ALLOWED_HOSTS=*` dans `.env.example` racine, aucun setting `SECURE_*` configuré (SSL redirect, HSTS, cookies sécurisés), nginx en HTTP uniquement sans headers de sécurité, containers Docker tournant en root. Le mot de passe par défaut `infoclimat2026` apparaît dans 5+ fichiers.

**Correctif court terme** :

- Remplacer `ALLOWED_HOSTS=*` par les domaines réels dans `.env.example`
- Ajouter les settings Django conditionnels en production :
  ```python
  if not DEBUG:
      SECURE_SSL_REDIRECT = True
      SESSION_COOKIE_SECURE = True
      CSRF_COOKIE_SECURE = True
      SECURE_HSTS_SECONDS = 31536000
  ```
- Ajouter un utilisateur non-root dans les Dockerfiles (`USER appuser`)
- Ajouter les headers sécurité dans `nginx.conf` (X-Frame-Options, X-Content-Type-Options, Referrer-Policy)

**Solution long terme** :

- Configurer HTTPS/TLS complet dans nginx avec Let's Encrypt (certbot)
- Mettre en place un **WAF** (Web Application Firewall) ou Cloudflare
- Externaliser les secrets dans un vault (HashiCorp Vault, AWS Secrets Manager, ou GitHub Environments)
- Implémenter un scan de sécurité automatisé dans la CI (Bandit + pip-audit + Trivy pour les images Docker)

**Outils / Technologies** :
| Outil | Rôle | Coût |
|-------|------|------|
| Let's Encrypt + certbot | Certificats TLS gratuits | Gratuit |
| `django-secure` / settings natifs | Headers sécurité Django | Gratuit |
| `bandit` | Scanner sécurité code Python | Gratuit |
| `pip-audit` | Audit vulnérabilités dépendances | Gratuit |
| `trivy` | Scan vulnérabilités images Docker | Gratuit |
| Cloudflare | WAF + CDN + DDoS protection | Gratuit (plan basique) |

---

### 4️⃣ #4 — Pas de rate limiting (Sécurité)

**Constat** : Aucune protection contre les abus, ni au niveau Django REST Framework (throttling), ni au niveau nginx (limit_req). L'API publique sans authentification est une cible facile pour du scraping massif ou du déni de service.

**Correctif court terme** :

- Configurer le throttling DRF dans `settings.py` :
  ```python
  REST_FRAMEWORK = {
      "DEFAULT_THROTTLE_CLASSES": [
          "rest_framework.throttling.AnonRateThrottle",
      ],
      "DEFAULT_THROTTLE_RATES": {
          "anon": "100/minute",
      },
  }
  ```
- Ajouter `limit_req_zone` et `limit_req` dans `nginx.conf`

**Solution long terme** :

- Implémenter un système d'**API keys** pour les consommateurs réguliers (quotas personnalisés)
- Ajouter un rate limiting distribué avec **Redis** (pour les déploiements multi-instances)
- Mettre en place du **request caching** nginx ou Django pour les endpoints fréquents
- Intégrer un CDN (Cloudflare) pour absorber le trafic en amont

**Outils / Technologies** :
| Outil | Rôle | Coût |
|-------|------|------|
| DRF Throttling | Rate limiting applicatif (natif) | Gratuit |
| nginx `limit_req` | Rate limiting réseau (natif) | Gratuit |
| Redis + `django-redis` | Rate limiting distribué + cache | Gratuit (self-hosted) |
| `djangorestframework-api-key` | Gestion d'API keys | Gratuit |
| Cloudflare | Protection DDoS en amont | Gratuit (plan basique) |

---

### 5️⃣ #5 — Zéro test frontend (Testing)

**Constat** : Malgré Vitest, @nuxt/test-utils, @vue/test-utils et @testing-library/vue déjà installés, aucun fichier de test n'existe. Les composables (useApiClient, useTemperature, useNationalIndicator…), le store Pinia (itnStore), et les composants sont totalement non testés. Toute régression frontend est silencieuse.

**Correctif court terme** :

- Écrire des tests unitaires pour les **composables** (`useApiClient`, `useCustomDate`, `useNationalIndicator`) — ce sont les plus critiques car ils contiennent la logique métier
- Écrire des tests pour le **store Pinia** (`itnStore`) — source de vérité de l'application
- Configurer le script `test:unit` dans la CI (workflow tests.yml)

**Solution long terme** :

- Couvrir les **composants UI** avec des tests de rendering (@testing-library/vue)
- Configurer **Playwright** pour des tests E2E (parcours utilisateur complets)
- Mettre en place du **visual regression testing** (Percy, Chromatic)
- Atteindre un seuil de coverage frontend minimum (60-70%)

**Outils / Technologies** :
| Outil | Rôle | Coût |
|-------|------|------|
| Vitest | Test runner (déjà installé) | Gratuit |
| @testing-library/vue | Tests composants (déjà installé) | Gratuit |
| @nuxt/test-utils | Helpers Nuxt pour tests (déjà installé) | Gratuit |
| Playwright | Tests E2E (déjà dans devDeps) | Gratuit |
| `@vitest/coverage-v8` | Coverage frontend | Gratuit |
| Percy / Chromatic | Visual regression testing | Payant |

---

## Matrice de Priorités

### 🔴 Critique — À traiter immédiatement

| #   | Action                                                     | Catégorie              | Effort |
| --- | ---------------------------------------------------------- | ---------------------- | ------ |
| 1   | Ajouter logging Django + Sentry + endpoint `/health`       | Monitoring             | Moyen  |
| 2   | Corriger `ALLOWED_HOSTS=*` dans .env.example               | Sécurité               | Faible |
| 3   | Ajouter HTTPS + headers sécurité dans nginx                | Sécurité + Déploiement | Moyen  |
| 4   | Configurer `SECURE_*` settings Django (SSL, HSTS, cookies) | Sécurité               | Faible |
| 5   | Containers non-root dans les Dockerfiles                   | Sécurité + Déploiement | Faible |
| 6   | Ajouter workflow CI pour pytest (gate avant merge)         | Testing                | Faible |

### 🟠 Élevé — Prochaine itération

| #   | Action                                         | Catégorie         | Effort |
| --- | ---------------------------------------------- | ----------------- | ------ |
| 7   | Ajouter rate limiting (DRF throttling + nginx) | Sécurité          | Faible |
| 8   | Écrire les tests frontend (infra déjà prête)   | Testing           | Élevé  |
| 9   | Configurer coverage + seuil minimum            | Testing           | Faible |
| 10  | docker-compose production + doc déploiement    | Déploiement + Doc | Moyen  |
| 11  | Tests gate avant déploiement staging           | Déploiement       | Faible |
| 12  | Prometheus + métriques applicatives            | Monitoring        | Moyen  |
| 13  | Runbook opérationnel                           | Documentation     | Moyen  |

### 🟡 Moyen — Planifier

| #   | Action                                  | Catégorie     | Effort |
| --- | --------------------------------------- | ------------- | ------ |
| 14  | Ajouter mypy + config stricte           | Code Quality  | Moyen  |
| 15  | Configurer Dependabot                   | Code Quality  | Faible |
| 16  | Tests contrat API (vs openapi.yaml)     | Testing       | Moyen  |
| 17  | Restreindre Django Admin (IP whitelist) | Sécurité      | Faible |
| 18  | CONTRIBUTING.md + CHANGELOG             | Documentation | Faible |
| 19  | Architecture Decision Records (ADR)     | Documentation | Moyen  |
| 20  | Ajouter Bandit au pre-commit            | Code Quality  | Faible |

### 🟢 Faible — Nice to have

| #   | Action                                 | Catégorie     | Effort |
| --- | -------------------------------------- | ------------- | ------ |
| 21  | Métriques de complexité (McCabe/radon) | Code Quality  | Faible |
| 22  | Tests E2E avec Playwright              | Testing       | Élevé  |
| 23  | Tests de charge (k6/Locust)            | Testing       | Moyen  |
| 24  | Backend Dockerfile multi-stage         | Déploiement   | Faible |
| 25  | Doc pipeline CI/CD                     | Documentation | Faible |
