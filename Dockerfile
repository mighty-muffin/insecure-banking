# Build stage
FROM python:3.10-alpine3.20@sha256:49eacd850181aa9cea2dcb38130386703bd63b67559085e18476b067e3af1070 AS builder

# Install uv - pinned to version 0.9.18 with SHA digest for reproducibility
COPY --from=ghcr.io/astral-sh/uv:0.9.18@sha256:5713fa8217f92b80223bc83aac7db36ec80a84437dbc0d04bbc659cae030d8c9 /uv /usr/local/bin/uv

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
FROM python:3.10-alpine3.20@sha256:49eacd850181aa9cea2dcb38130386703bd63b67559085e18476b067e3af1070

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
