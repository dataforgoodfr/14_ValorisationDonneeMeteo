# System Audit

## Summary

This document summarises current gaps and an improvement plan across the following categories: Code Quality, Testing, Deployment Process, Monitoring, Security and Documentation.

---

## Code Quality

### Missing

- Règles de style / linter appliquées systématiquement
- Checks de types (`mypy` / TypeScript)
- Quality gates (coverage minimum)
- Analyse statique et SCA intégrée

## Summary

Ce document résume les lacunes actuelles et propose un plan d'amélioration couvrant les catégories suivantes : Code Quality, Testing, Deployment Process, Monitoring, Security et Documentation.

### Manuel vs Automatisé

### Manual vs Automated

- Automatisé : linting et tests unitaires dans la CI
- Manuel : revues de code et approbations

### Potential failure points

### Potential failure points

- Merges sans revue ni gate
- Détérioration due aux dépendances
- Absence de vérifications locales (les devs ignorent les erreurs)
- Absence de checks locaux (devs ignorent les erreurs)

### Improvement Plan

- Correctif court terme : ajouter des hooks `pre-commit` (format + lint), une configuration minimale `ruff`/`flake8` et `black`, et exiger une revue avant merge.
- Solution long terme : instaurer des quality gates en CI (lint, `mypy`, seuil de couverture), revue régulière des dépendances et conventions de design, formation des développeurs.
- Outils / technologies : `pre-commit`, `ruff`/`flake8`, `black`, `isort`, `mypy`, GitHub Actions / GitLab CI, Dependabot / Renovate, Snyk.
- Long-term solution: quality gates en CI (lint, `mypy`, seuil de coverage), revue régulière des dépendances et conventions de design, formation devs.
- Tools/technologies: `pre-commit`, `ruff`/`flake8`, `black`, `isort`, `mypy`, GitHub Actions / GitLab CI, Dependabot / Renovate, Snyk.

### Manual vs Automated

- Automatisé : tests unitaires et certains tests d'intégration dans la CI
- Manuel : tests e2e et vérifications ad-hoc

## Testing

### Potential failure points

- Tests instables bloquant la CI
- Environnement CI différent de la prod
- Couverture insuffisante pour les chemins critiques
- Tests d'intégration répétés
- Tests end-to-end

### Improvement Plan

- Correctif court terme : ajouter des tests unitaires pour les modules critiques, exécuter `pytest` en CI ; ajouter des fixtures pour la DB et un profil de test local.
- Solution long terme : définir une stratégie complète (unit, integration, e2e), matrice CI (OS / versions), pipeline pour e2e stabilisés et plan de réduction des tests flaky.
- Outils / technologies : `pytest`, `pytest-xdist`, `tox`/`nox`, Docker Compose pour fixtures, Playwright / Cypress pour e2e, CI (GitHub Actions/GitLab CI).

### Manuel vs Automatisé

### Manual vs Automated

- Automatisé : builds d'images
- Manuel : promotions vers staging/prod et exécution des migrations
- Manuel: tests e2e et vérifications ad-hoc

### Potential failure points

- Migrations cassées en production
- Erreurs humaines lors de déploiements manuels
- Images non immuables et dérive de configuration
- Environnement CI différent de prod
- Couverture insuffisante pour chemins critiques

### Improvement Plan

- Correctif court terme : fournir des scripts reproductibles de build et déploiement ainsi qu'une checklist de release ; automatiser le build d'images avec tagging sémantique.
- Solution long terme : mettre en place du CD (blue/green ou canary), rollback automatisé, infra-as-code (Terraform) et migrations sécurisées.
- Outils / technologies : pipelines CI/CD (GitHub Actions / GitLab CI / ArgoCD), registry (GHCR/ECR), Terraform, Flyway / mécanismes de migration sûrs, Helm.
- Short-term fix: ajouter tests unitaires pour modules critiques, exécuter `pytest` en CI; ajouter fixtures DB et profil de test local.
- Long-term solution: stratégie complète (unit/integration/e2e), matrice CI, pipeline pour e2e stabilisés, réduire flakys.

### Manual vs Automated

- Automatisé : collecte des métriques et des logs si les agents sont déployés
- Manuel : réglage des alertes et réponses aux incidents

---

### Potential failure points

- Alertes manquantes ou trop bruyantes
- Logs insuffisants pour une RCA complète
- Absence de supervision des jobs batch/cron

- Pipeline CD (déploiement automatisé)

### Improvement Plan

- Correctif court terme : instrumenter l'application pour exposer des métriques de base, centraliser les logs (niveau INFO+) et configurer des alertes simples sur erreurs et latence.
- Solution long terme : définir des SLO/SLA, implémenter le tracing distribué, dashboards et playbooks d'incident, et automatiser des tests d'alerte.
- Outils / technologies : Prometheus, Grafana, Loki, OpenTelemetry, Alertmanager, Sentry.
- Migrations automatisées et safe-run

### Manual vs Automated

- Automatisable : SCA et scans statiques dans la CI
- Manuel : remédiation, patching et audits
- Automatisé: builds d'images
- Manuel: promotions staging/prod et migrations

### Potential failure points

- Secrets committés dans le VCS
- Dépendances vulnérables non patchées
- Permissions excessives en base de données ou dans les containers
- Migrations cassées en prod
- Erreurs humaines lors de déploiement manuel

### Improvement Plan

- Correctif court terme : activer les scans SCA en CI, rechercher les secrets committés et procéder à une rotation si nécessaire ; restreindre les variables sensibles.
- Solution long terme : mettre en place une gestion centralisée des secrets (Vault), RBAC, un backlog de remédiation CVE et une politique de patching régulière, ainsi que des audits périodiques.
- Outils / technologies : Dependabot / Renovate, Snyk / Trivy, GitLeaks / detect-secrets, HashiCorp Vault / AWS Secrets Manager, OPA.

- Short-term fix: scripts reproductibles de build/déploiement et checklist de release; automatiser builds d'images avec tags semver.

### Manual vs Automated

- Automatisable : génération des specs API
- Manuel : guides, runbooks et mises à jour

---

### Potential failure points

- Documentation obsolète entraînant des erreurs en production
- Absence de runbook pendant un incident
- Manque de centralisation des documents

### Missing

### Improvement Plan

- Correctif court terme : ajouter des runbooks essentiels (démarrage/arrêt, rollback, accès DB), un README d'installation pour les développeurs et une checklist de release.
- Solution long terme : maintenir une documentation centralisée (architecture, runbooks, onboarding), automatiser la génération des specs API et lier la mise à jour des docs aux PRs.
- Outils / technologies : MkDocs / Docusaurus, OpenAPI generator, PlantUML, job CI de validation des docs.
- Logs centralisés et tracing distribué

### Manuel vs Automatisé

- Automatisé: collecte métriques/logs si agents déployés

## Priorities (short term)

1. CI : linter + tests unitaires automatisés
2. Sécurité : scan SCA + détection des secrets dans le VCS
3. Observabilité : métriques basiques + logs centralisés
4. Déploiement : scripts reproductibles, tagging d'images et migrations sécurisées
5. Documentation opérationnelle : runbooks essentiels + README dev

- Manuel: tuning des alertes et réponse incident

### Potential failure points

- Alertes manquantes ou bruyantes
- Logs insuffisants pour RCA
- Pas de monitoring des jobs batch/cron

### Improvement Plan

- Short-term fix: instrumenter pour métriques basiques, centraliser logs (niveau INFO+), configurer alertes simples sur erreurs/latency.
- Long-term solution: définir SLOs, tracing distribué, dashboards et playbooks d'incident, tests d'alerte réguliers.
- Tools/technologies: Prometheus, Grafana, Loki, OpenTelemetry, Alertmanager, Sentry.

---

## Security

### Missing

- Scanning CVE des dépendances
- Scanning secrets dans le VCS
- Gestion des credentials (Vault / secret manager)
- Revues de sécurité et RBAC
- Tests d'intrusion / audits

### Manuel vs Automatisé

- Automatisable: SCA et scans statiques en CI
- Manuel: remédiation, patching, audits

### Potential failure points

- Secrets committés
- Dépendances vulnérables non patchées
- Permissions excessives en DB / containers

### Improvement Plan

- Short-term fix: activer SCA en CI, rechercher secrets committés et tourner si trouvés; restreindre variables sensibles.
- Long-term solution: gestion centralisée des secrets (Vault), RBAC, backlog de remédiation CVE et politique de patching, audits réguliers.
- Tools/technologies: Dependabot / Renovate, Snyk / Trivy, GitLeaks / detect-secrets, HashiCorp Vault / AWS Secrets Manager, OPA.

---

## Documentation

### Missing

- Runbooks d'exploitation et procédures d'urgence
- Architecture & diagrammes
- Guide d'onboarding dev
- API docs à jour
- Procédures de déploiement et checklist de release

### Manuel vs Automatisé

- Automatisable: génération de specs API
- Manuel: guides, runbooks, mises à jour

### Potential failure points

- Docs obsolètes menant à erreurs en prod
- Absence de runbook pendant incident
- Manque de centralisation

### Improvement Plan

- Short-term fix: ajouter runbooks essentiels (start/stop, rollback, accès DB), README dev et checklist de release.
- Long-term solution: docs centralisées (architecture, runbooks, onboarding), automatiser génération d'API specs et lier aux PRs.
- Tools/technologies: MkDocs / Docusaurus, OpenAPI generator, PlantUML, job CI de validation docs.

---

## Priorités recommandées (court terme)

1. CI: linter + tests unitaires
2. Sécurité: SCA scan + secrets scan
3. Observabilité: metrics basiques + logs centralisés

---

_Ajouté le :_ `2026-03-05`
