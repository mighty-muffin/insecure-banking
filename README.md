# Insecure Bank (python)

## 🚀 Deploy to Azure (Recommended)

Deploy this application to Azure Container Instances with optional Cloudflare domain in minutes!

```bash
cd deploy
chmod +x deploy-azure.sh
./deploy-azure.sh
```

See [Quick Start Guide](deploy/QUICKSTART.md) for step-by-step instructions and [Deployment Guide](deploy/DEPLOYMENT.md) for detailed configuration options.

### Features
- ✅ One-command deployment to Azure
- ✅ Automatic Docker image building and hosting
- ✅ Public URL with automatic DNS
- ✅ Optional Cloudflare domain integration
- ✅ Easy HTTPS setup with Cloudflare

## Running the application locally

1. Build and run the application:

   ```bash
   uv venv .venv --python 3.10
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

## Running with Docker Compose

```bash
docker-compose up -d
```

Access at <http://localhost:8000>

## Login credentials

```text
Username: john
Password: test
```
