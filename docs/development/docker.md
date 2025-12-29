# Docker Deployment

## Prerequisites

Ensure Docker is installed on your system. Verify installation:

```bash
docker --version
```

## Building the Docker Image

Build the Docker image with build arguments:

```bash
docker build \
  --build-arg GIT_COMMIT=$(git rev-parse --short HEAD) \
  --build-arg REPO_URL=$(git config --get remote.origin.url | sed 's/git@/https:\/\//; s/.com:/.com\//; s/\.git$//') \
  --file Dockerfile \
  --tag insecure-bank-py .
```

### Build Arguments

- `GIT_COMMIT`: Embeds the current Git commit hash into the image
- `REPO_URL`: Embeds the repository URL into the image

## Running the Container

Stop and remove any existing container, then run a new one:

```bash
docker stop insecure-bank-py && docker rm insecure-bank-py
docker run --detach --publish 8000:8000 --name insecure-bank-py insecure-bank-py
```

### Run Options

- `--detach`: Run container in background
- `--publish 8000:8000`: Map port 8000 from container to host
- `--name insecure-bank-py`: Assign a name to the container

## Accessing the Application

Open your browser and navigate to [http://localhost:8000](http://localhost:8000).

## Viewing Logs

View container logs:

```bash
docker logs insecure-bank-py
```

Follow logs in real-time:

```bash
docker logs -f insecure-bank-py
```

## Container Management

### Stop Container

```bash
docker stop insecure-bank-py
```

### Start Stopped Container

```bash
docker start insecure-bank-py
```

### Remove Container

```bash
docker rm insecure-bank-py
```

### Remove Image

```bash
docker rmi insecure-bank-py
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, map to a different port:

```bash
docker run --detach --publish 8080:8000 --name insecure-bank-py insecure-bank-py
```

### Container Fails to Start

Check container logs for error messages:

```bash
docker logs insecure-bank-py
```

### Build Cache Issues

Force a clean build without cache:

```bash
docker build --no-cache --file Dockerfile --tag insecure-bank-py .
```

## Docker Compose

For future enhancements, consider using Docker Compose to manage multi-container deployments or additional services like databases.
