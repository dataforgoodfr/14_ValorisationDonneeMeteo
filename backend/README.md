# Backend

## Prérequis

- Python 3.x
- [uv](https://docs.astral.sh/uv/) pour la gestion des dépendances

## Installation

```bash
cd backend
uv sync
```

## Activation de l'environnement

Avec VSCode, l'environnement virtuel est activé automatiquement.

Sinon :

```bash
source .venv/bin/activate
```

Ou utilisez `uv run` pour exécuter directement :

```bash
uv run python script.py
```

## Lancer les pre-commit hooks

```bash
pre-commit run --all-files
```

## Tests

```bash
tox -vv
```
