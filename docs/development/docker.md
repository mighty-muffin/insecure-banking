# Docker Containerization

## Dockerfile

Multi-stage Docker build for optimized images.

### Build Stage

```dockerfile
FROM python:3.10-alpine3.20 AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1

# Install build dependencies
RUN apk add --no-cache build-base libffi-dev

# Install Python dependencies
COPY requirements.txt .
RUN uv venv /app/.venv
RUN uv pip install -r requirements.txt
```

### Runtime Stage

```dockerfile
FROM python:3.10-alpine3.20

# Build arguments
ARG GIT_COMMIT="unknown"
ARG REPO_URL=""

# Environment variables
ENV GIT_COMMIT=${GIT_COMMIT}
ENV REPO_URL=${REPO_URL}
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Install runtime dependencies
RUN apk add --no-cache tini libffi

# Copy virtual environment and code
COPY --from=builder /app/.venv /app/.venv
COPY src /app/src

# Set ownership
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Run migrations
RUN python src/manage.py migrate

# Start application
ENTRYPOINT ["tini", "--"]
CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]
```

## Build Features

### Multi-Stage Build

Separates build and runtime dependencies:
- Smaller final image
- Faster deployment
- Better security

### Alpine Base

Uses Alpine Linux for minimal image size:
- Small footprint (~50MB base)
- Security-focused
- Fast downloads

### Non-Root User

Runs as non-root for security:
```dockerfile
USER appuser
```

### Init System

Uses tini as PID 1:
- Proper signal handling
- Zombie process reaping
- Graceful shutdown

### Build Arguments

Injects metadata:
- GIT_COMMIT: Commit SHA
- REPO_URL: Repository URL

## Building Images

### Basic Build

```bash
docker build -t insecure-bank-py .
```

### With Metadata

```bash
docker build \
  --build-arg GIT_COMMIT=$(git rev-parse --short HEAD) \
  --build-arg REPO_URL=$(git config --get remote.origin.url | sed 's/git@/https:\/\//; s/.com:/.com\//; s/\.git$//') \
  --tag insecure-bank-py \
  .
```

### No Cache

```bash
docker build --no-cache -t insecure-bank-py .
```

## Running Containers

### Detached Mode

```bash
docker run -d -p 8000:8000 --name insecure-bank-py insecure-bank-py
```

### Interactive Mode

```bash
docker run -it -p 8000:8000 insecure-bank-py
```

### With Volume

```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/src:/app/src \
  insecure-bank-py
```

### With Environment Variables

```bash
docker run -d \
  -p 8000:8000 \
  -e DEBUG=False \
  -e SECRET_KEY=production-key \
  insecure-bank-py
```

## Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
    volumes:
      - ./src:/app/src
```

Run:
```bash
docker-compose up
```

## Image Optimization

### Layer Caching

Order instructions from least to most frequently changing:
1. Base image
2. System dependencies
3. Python dependencies
4. Application code

### Size Reduction

- Multi-stage builds
- Alpine base image
- Clean up in same layer
- Minimal runtime dependencies

## Container Registry

### GitHub Container Registry

Push to GHCR:
```bash
docker tag insecure-bank-py ghcr.io/mighty-muffin/insecure-banking:latest
docker push ghcr.io/mighty-muffin/insecure-banking:latest
```

### Pull Image

```bash
docker pull ghcr.io/mighty-muffin/insecure-banking:latest
```

## Security

### Non-Root User

Container runs as appuser:
```dockerfile
USER appuser
```

### Read-Only Filesystem

Can be enforced at runtime:
```bash
docker run --read-only insecure-bank-py
```

### Security Scanning

Scan for vulnerabilities:
```bash
docker scan insecure-bank-py
```

## Troubleshooting

### View Logs

```bash
docker logs insecure-bank-py
```

### Shell Access

```bash
docker exec -it insecure-bank-py sh
```

### Rebuild

```bash
docker build --no-cache -t insecure-bank-py .
```

## Related Documentation

- [Development Setup](setup.md)
- [Running the Application](running.md)
- [CI/CD Overview](../cicd/overview.md)
