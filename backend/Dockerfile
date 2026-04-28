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

RUN uv sync --locked

EXPOSE 8000
CMD ["/app/.venv/bin/gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--worker-tmp-dir", "/dev/shm", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info"]
