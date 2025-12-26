# Build stage
FROM python:3.13-alpine3.20 AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1

RUN apk add --no-cache build-base libffi-dev

COPY requirements.txt .

# Create virtual environment and install dependencies
RUN uv venv /app/.venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

RUN uv pip install -r requirements.txt

# Runtime stage
FROM python:3.13-alpine3.20

ARG GIT_COMMIT="unknown"
ARG REPO_URL=""

ENV GIT_COMMIT=${GIT_COMMIT}
ENV REPO_URL=${REPO_URL}

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Create a non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Install runtime dependencies
RUN apk add --no-cache tini libffi

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src /app/src

# Set ownership
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Run migrations
RUN python src/manage.py migrate

ENTRYPOINT ["tini", "--"]
CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]
