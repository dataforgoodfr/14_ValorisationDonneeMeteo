# Intégration continue (GitHub Actions)

Ce dépôt utilise le workflow [`.github/workflows/ci.yml`](../.github/workflows/ci.yml). Il se déclenche sur chaque push et sur chaque pull request vers toutes les branches.

## Étapes du pipeline

| Étape | Backend | Frontend |
|--------|---------|----------|
| Dépendances | `uv sync --extra dev` | `npm install` |
| Lint | Ruff (check + format) | ESLint |
| Tests | pytest + JUnit + couverture XML | Vitest + JUnit + LCOV |
| Audit dépendances | `pip-audit` (fichier `pip-audit.txt`) | `npm audit` (fichier `npm-audit.txt`) |
| Scan fichiers | Trivy `fs` sur `backend/` | Trivy `fs` sur `frontend/` |
| Docker | Build + push GHCR **uniquement** sur push vers `main` | Idem |

Les images sont publiées sous `ghcr.io/<org>/<repo>/backend` et `ghcr.io/<org>/<repo>/frontend` (tags `latest` et SHA du commit).

## Artefacts (rapports)

Après chaque exécution, télécharge les rapports depuis GitHub : **Actions** → exécution du workflow **CI** → section **Artifacts**.

- `backend-reports-<sha>` : JUnit, `coverage-backend.xml`, sorties pip-audit et Trivy.
- `frontend-reports-<sha>` : JUnit, `coverage/lcov.info`, sorties npm audit et Trivy.

Les fichiers sont conservés 14 jours.

## SonarCloud (analyse qualité / « SonarQube »)

1. Crée un compte sur [SonarCloud](https://sonarcloud.io) et importe ce dépôt GitHub (ou crée un projet manuellement).
2. Dans **Administration → Project Information**, note `Organization Key` et `Project Key`.
3. Copie ces valeurs dans [`sonar-project.properties`](../sonar-project.properties) (`sonar.organization`, `sonar.projectKey`).
4. Dans GitHub : **Settings → Secrets and variables → Actions**, ajoute le secret **`SONAR_TOKEN`** (token généré dans SonarCloud : **My Account → Security**).
5. Dans **Settings → Secrets and variables → Actions → Variables**, ajoute **`SONAR_ENABLED`** = `true` pour activer le job Sonar dans le workflow.

Sans `SONAR_ENABLED=true`, le job Sonar est ignoré (le reste du pipeline continue). Le job Sonar ne s’exécute pas sur les pull requests ouvertes depuis un fork (les secrets ne sont pas exposés dans ce cas sur GitHub).

## Secrets utilisés

| Nom | Rôle |
|-----|------|
| `GITHUB_TOKEN` | Fourni par GitHub : login GHCR, analyse Sonar avec lien PR (automatique). |
| `SONAR_TOKEN` | Analyse SonarCloud (à créer côté SonarCloud). |

## Exercice : casser volontairement un test

1. Crée une branche depuis `main` (ex. `chore/ci-test-break`).
2. Modifie un test pour qu’il échoue (assert fausse, valeur attendue incorrecte).
3. Pousse la branche et ouvre une PR : le workflow **CI** doit être **rouge** sur l’étape de tests.
4. Corrige le test, pousse : le workflow doit repasser au **vert**.

Documente ce scénario dans ton compte-rendu (captures d’écran possibles).

## Bonnes pratiques Git (rappel)

Branches depuis `main`, PR avec template, commits et messages structurés : voir [README principal](../README.md#workflow-de-contribution).
