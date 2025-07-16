# Builder stage 
FROM python:3.12-bookworm AS builder
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes pipx

RUN pipx install uv 
ENV UV_CACHE_DIR=/tmp/uv_cache \
    PATH="/root/.local/bin:${PATH}"

WORKDIR /src
COPY pyproject.toml .
COPY . .
RUN uv sync
RUN pip install .
 

# Runtime stage 
FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \ 
    && rm -rf /var/lib/apt/lists/*
ENV PATH="/src/.venv/bin:$PATH"
ENV DB_HOST="localhost"
ENV DB_USER="postgres"
ENV DB_PASSWORD="password"
ENV DB_NAME="omop"
ENV DB_PORT=5432
ENV DB_SCHEMA="public"
ENV DB_VECTABLE="embeddings"
ENV DB_VECSIZE=384
WORKDIR /src
COPY --from=builder /src/.venv /src/.venv

LABEL org.opencontainers.image.title=Lettuce
LABEL org.opencontainers.image.description=lettuce-dev-base 
LABEL org.opencontainers.image.vendor=University\ of\ Nottingham
LABEL org.opencontainers.image.url=https://github.com/Health-Informatics-UoN/lettuce/pkgs/container/lettuce
LABEL org.opencontainers.image.documentation=https://health-informatics-uon.github.io/lettuce/
LABEL org.opencontainers.image.source=https://github.com/Health-Informatics-UoN/lettuce
LABEL org.opencontainers.image.licenses=MIT

COPY . .
EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
