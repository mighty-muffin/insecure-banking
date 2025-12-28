# Build stage
FROM python:3.10.11-alpine3.18 AS builder

COPY --from=ghcr.io/astral-sh/uv:0.9.18@sha256:5713fa8217f92b80223bc83aac7db36ec80a84437dbc0d04bbc659cae030d8c9 /uv /usr/local/bin/uv

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1

RUN apk add --no-cache build-base libffi-dev

COPY requirements.txt .

RUN uv venv /app/.venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

RUN uv pip install -r requirements.txt

# Runtime stage
FROM python:3.10.11-alpine3.18 AS runtime

ARG GIT_COMMIT="unknown"
ARG REPO_URL=""

ENV GIT_COMMIT=${GIT_COMMIT}
ENV REPO_URL=${REPO_URL}

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

RUN apk add --no-cache curl libffi tini

COPY --from=builder /app/.venv /app/.venv

COPY src /app/src
COPY manage.py /app/manage.py

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

RUN python manage.py migrate

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/login || exit 1

ENTRYPOINT ["tini", "--"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
