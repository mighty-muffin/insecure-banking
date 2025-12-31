# Dev Container Setup

This directory contains the configuration for a VS Code dev container optimized for Python 3.10 web development with uv.

## What's Included

### Tools & Extensions

- **Python 3.10**: The runtime environment
- **uv**: Fast Python package installer and resolver
- **Docker CLI**: For building and managing containers
- **Git & GitHub CLI**: Version control tools
- **VS Code Extensions**:
  - Python & Pylance (language support)
  - Ruff (formatting & linting)
  - Docker (container management)
  - GitHub Copilot (AI pair programming)
  - TOML & YAML support

### Features

- Automatic virtual environment creation with uv
- Pre-configured Python settings (formatting, linting, testing)
- Port forwarding for Django dev server (8000)
- Docker-in-Docker support via socket mounting
- Playwright for E2E testing
- Pre-commit hooks setup

## Getting Started

### Prerequisites

- [Visual Studio Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Opening the Dev Container

1. Open this project in VS Code
2. Press `F1` and select **Dev Containers: Reopen in Container**
3. Wait for the container to build (first time takes a few minutes)
4. The `postCreateCommand` will automatically set up your environment

### What Happens Automatically

When the container is created:

1. Virtual environment is created at `.venv/`
2. All dependencies are installed via uv
3. Playwright browsers are installed
4. Pre-commit hooks are configured
5. Database migrations are run
6. A `.env` file is created (if it doesn't exist)

## Usage

### Running the Development Server

```bash
python manage.py runserver 0.0.0.0:8000
```

The server will be available at <http://localhost:8000>

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# E2E tests
pytest tests/e2e/

# With coverage
pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

### Working with Dependencies

```bash
# Add a new dependency
uv pip install package-name

# Update requirements.txt
uv pip freeze > requirements.txt

# Or use uv's export
uv export --no-dev --output-file requirements.txt
```

### Docker Commands

Since Docker CLI is installed, you can build and manage containers:

```bash
# Build the production Docker image
docker build -t insecure-banking .

# Run the production container
docker run -p 8000:8000 insecure-banking
```

## Customization

### Adding VS Code Extensions

Edit `.devcontainer/devcontainer.json` and add extension IDs to the `extensions` array:

```json
"extensions": [
  "publisher.extension-name"
]
```

### Changing Python Settings

Edit the `settings` object in `.devcontainer/devcontainer.json`.

### Adding System Packages

Edit `.devcontainer/Dockerfile` and add packages to the `apt-get install` command.

## Troubleshooting

### Container Won't Build

- Make sure Docker Desktop is running
- Try rebuilding without cache: `F1` → **Dev Containers: Rebuild Container Without Cache**

### Dependencies Not Installing

- Check if `requirements.txt` and `pyproject.toml` are valid
- Rebuild the container
- Manually run: `uv pip install -r requirements.txt`

### Database Issues

- Delete `db.sqlite3` and restart the container
- Or manually run: `python manage.py migrate`

### Port Already in Use

- Change the port in `devcontainer.json` under `forwardPorts`
- Or stop the process using port 8000 on your host

## Benefits of This Setup

✅ **Consistent Environment**: Everyone uses the same Python version and dependencies
✅ **Fast Setup**: New team members can start coding in minutes
✅ **Isolated**: No conflicts with other Python projects on your machine
✅ **Reproducible**: Same environment locally and in CI/CD
✅ **Pre-configured**: Linting, formatting, testing all ready to go
✅ **Modern Tools**: uv is significantly faster than pip

## Learn More

- [Dev Containers Documentation](https://code.visualstudio.com/docs/devcontainers/containers)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Django Documentation](https://docs.djangoproject.com/)
