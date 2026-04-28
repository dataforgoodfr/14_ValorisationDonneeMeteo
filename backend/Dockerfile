# ══════════════════════════════════════════════════════════════
# Stage 1 — Builder
# Image DHI avec shell pour compiler les dépendances
# ══════════════════════════════════════════════════════════════
FROM dhi.io/python:3.12-debian13-dev AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_NO_DEV=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copier uv depuis son image officielle
COPY --from=ghcr.io/astral-sh/uv:0.10.0 /uv /uvx /bin/

# Copier les fichiers de dépendances d'abord (cache Docker)
COPY pyproject.toml uv.lock ./

# Installer les dépendances sans le projet
RUN uv sync --locked --no-install-project

# Copier le reste du code
COPY . .

# Installer le projet complet
RUN uv sync --locked

# Rendre l'entrypoint exécutable ici (le runtime n'a pas de shell)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# ══════════════════════════════════════════════════════════════
# Stage 2 — Runtime
# Image DHI distroless — pas de shell, surface d'attaque minimale
# ══════════════════════════════════════════════════════════════
FROM dhi.io/python:3.12-debian13 AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copier le venv, le code et l'entrypoint depuis le builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app
COPY --from=builder /entrypoint.sh /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/app/.venv/bin/gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]