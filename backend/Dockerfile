ARG PYTHON_BASE_IMAGE=python:3.12-slim-bookworm
FROM ${PYTHON_BASE_IMAGE}

WORKDIR /app
RUN pip install --no-cache-dir uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/home/app \
    UV_CACHE_DIR=/home/app/.cache/uv

COPY . .
RUN uv sync --no-dev

RUN addgroup --system app && adduser --system --ingroup app app
RUN mkdir -p /home/app/.cache/uv
RUN sed -i 's/\r$//' /app/entrypoint.sh && chown -R app:app /app /home/app && chmod +x /app/entrypoint.sh

USER app

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
EXPOSE 8000
CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
