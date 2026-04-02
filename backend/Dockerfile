FROM dhi.io/python:3.12-dev AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_NO_DEV=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

COPY --from=ghcr.io/astral-sh/uv:0.10.0 /uv /bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

COPY . .
RUN uv sync --locked

FROM dhi.io/python:3.12 AS final

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/config ./config
COPY --from=builder /app/weather ./weather
COPY --from=builder /app/manage.py ./manage.py
COPY --from=builder /app/pyproject.toml ./pyproject.toml

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]
