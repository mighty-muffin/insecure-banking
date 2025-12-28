# Build stage
FROM python:3.10.11-alpine3.18 AS builder

COPY --from=ghcr.io/astral-sh/uv:0.9.18@sha256:5713fa8217f92b80223bc83aac7db36ec80a84437dbc0d04bbc659cae030d8c9 /uv /usr/local/bin/uv

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt .

# Install build dependencies, create venv, install packages, and cleanup in one layer
RUN apk add --no-cache build-base libffi-dev && \
    uv venv /app/.venv && \
    uv pip install -r requirements.txt && \
    apk del build-base && \
    rm -rf /root/.cache

# Runtime stage
FROM python:3.10.11-alpine3.18 AS runtime

ARG GIT_COMMIT="unknown"
ARG REPO_URL=""

ENV GIT_COMMIT=${GIT_COMMIT} \
    REPO_URL=${REPO_URL} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Create user and install runtime dependencies in one layer
RUN addgroup -S appgroup && adduser -S appuser -G appgroup && \
    apk add --no-cache curl libffi tini

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src /app/src
COPY manage.py /app/manage.py

# Set ownership
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/login || exit 1

ENTRYPOINT ["tini", "--"]
# Run migrations at startup, then start server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
