FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       unixodbc \
       unixodbc-dev \
       curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/pyproject.toml
COPY src /app/src
RUN pip install --no-cache-dir /app

COPY catalogs/aggregate-catalog.yaml /app/catalogs/aggregate-catalog.yaml
COPY catalogs/category-index.yaml /app/catalogs/category-index.yaml

ENV PYTHONPATH=/app/src
CMD ["python", "-m", "swarm_powerbi_bot.main"]
