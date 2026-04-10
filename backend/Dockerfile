FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# System deps (build + runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
  && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy dependency files first for caching
COPY pyproject.toml /app/pyproject.toml

# Install deps (no venv inside container)
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --no-root

# Copy app code
COPY app /app/app
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini

# Create upload dir (mounted in compose)
RUN mkdir -p /data/uploads

EXPOSE 8000

# PORT is set by Render (and other PaaS); falls back to 8000 for local/compose
ENV PORT=8000

# Run migrations then start API
CMD ["bash", "-lc", "alembic -c /app/alembic.ini upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]