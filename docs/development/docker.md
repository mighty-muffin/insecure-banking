# Docker Deployment

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
  --no-cache --file Dockerfile \
  --tag insecure-bank .
```

This command will build the container with:

- `GIT_COMMIT`: Embeds the current Git commit hash into the image
- `REPO_URL`: Embeds the repository URL into the image

## Running the Container

Stop and remove any existing container, then run a new one:

```bash
docker stop insecure-bank && docker rm insecure-bank
docker run --detach --publish 8000:8000 --name insecure-bank insecure-bank
```

This command will run the container with:

- `--detach`: Run container in background.
- `--publish 8000:8000`: Map port 8000 from container to host.
- `--name insecure-bank`: Assign a name to the container.
- The application will be available at [http://localhost:8000](http://localhost:8000).
- Use the following credentials to log into the application:
  - **Username**: john
  - **Password**: test
