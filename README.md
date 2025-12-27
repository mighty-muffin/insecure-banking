# Insecure Bank (python)

## Running the application locally

1. Build and run the application:

   ```bash
   uv venv .venv --python 3.10
   uv sync --all-extras --dev --frozen
   python src/manage.py migrate
   python src/manage.py runserver
   ```

2. You can then access the bank application here: <http://localhost:8000>

## Running with Docker

1. Build and run the application with Docker.

   ```bash
   docker build \
     --build-arg GIT_COMMIT=$(git rev-parse --short HEAD) \
     --build-arg REPO_URL=$(git config --get remote.origin.url | sed 's/git@/https:\/\//; s/.com:/.com\//; s/\.git$//') \
     --file Dockerfile --no-cache --tag insecure-bank-py .
   docker stop insecure-bank-py && docker rm insecure-bank-py
   docker run --detach --publish 8000:8000 --name insecure-bank-py insecure-bank-py
   docker logs insecure-bank-py
   ```

2. Open the application here: <http://localhost:8000>

## Login credentials

```text
Username: john
Password: test
```

## Testing

### Unit and Integration Tests

Run unit and integration tests with pytest:

```bash
pytest tests/ -m "not e2e"
```

### End-to-End Tests

Run end-to-end tests with Playwright:

```bash
# Make sure the application is running first
python src/manage.py runserver

# In a separate terminal, run e2e tests
pytest tests/e2e/ -p no:django -m e2e --no-cov
```

For more details on e2e testing, see [tests/e2e/README.md](tests/e2e/README.md).
