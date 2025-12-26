# Insecure Bank (python)

## Running the application locally

1. Build and run the application:

   ```bash
   uv venv --python 3.10
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
   docker run insecure-bank-py --detach --publish 8000:8000 --name insecure-bank-py
   docker logs insecure-bank-py
   ```

2. Open the application here: <http://localhost:8000>

## Login credentials

```text
Username: john
Password: test
```
