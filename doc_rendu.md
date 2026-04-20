# Doc rendu

## CI

La CI est dans :

```txt
.github/workflows/ci.yml
```

Elle fait :

- install backend et frontend
- lint
- tests
- scan securite
- scan Trivy
- fichier VEX
- build Docker
- push registry uniquement sur main

Pour tester :

```txt
GitHub > Actions > CI > Run workflow
```

Pour tester un test casse :

```txt
Run workflow avec break_test = true
```

Pour tester que ca repasse :

```txt
Run workflow avec break_test = false
```

Les rapports sont dans les artifacts du run GitHub Actions.

## Docker normal

Build local classique :

```bash
docker compose -f docker-compose.dev.yml build backend frontend
```

Lancer le projet :

```bash
docker compose -f docker-compose.dev.yml up --build
```

## Docker Hardened Images

Se connecter a DHI :

```bash
docker login dhi.io
```

Tester l'acces aux images :

```bash
docker pull dhi.io/python:3.12.13-debian13-dev
docker pull dhi.io/python:3.12.13-debian13
docker pull dhi.io/node:24-alpine3.23-dev
docker pull dhi.io/node:24-alpine3.23
```

Builder avec les images DHI :

```bash
docker compose -f docker-compose.dev.yml -f docker-compose.dhi.yml build backend frontend
```

Verifier les images :

```bash
docker images | grep 'meteo-.*dhi'
```

Images attendues :

```txt
meteo-backend:dhi
meteo-frontend:dhi
```

## Prometheus

Lancer le compose :

```bash
docker compose -f docker-compose.dev.yml up --build
```

Ouvrir :

```txt
http://localhost:9090
```

Verifier :

```txt
Status > Target health
```

Targets attendues :

```txt
prometheus
backend
```

## Grafana

Ouvrir :

```txt
http://localhost:3000
```

Identifiants :

```txt
admin / admin
```

Dashboard attendu :

```txt
Observability Overview
```
