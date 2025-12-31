---
hide:
  - toc
---
# Development Setup

Before setting up the development environment, ensure you have the following installed:

- Docker
- Git
- Python 3.10.x
- uv

## Installing package manager

If you do not have `uv` installed, install it using the official installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For other installation methods, refer to the [uv documentation](https://docs.astral.sh/uv/).

### Virtual Environment

Create and activate a virtual environment using uv:

```bash
uv venv .venv --python 3.10
source .venv/bin/activate
uv sync --all-extras --dev --frozen
uv sync --group docs  # If you want to create the documentation
```

This command will:

- Install all production dependencies
- Install development dependencies (testing, linting, etc.)
- Install documentation dependencies (mkdocs, mkdocs-material)
- Lock dependencies to ensure reproducible builds

## Database Setup

Initialize the database with migrations:

```bash
uv run python manage.py migrate
uv run python manage.py check
```

This command will:

- This will create the SQLite database file (`db.sqlite3`) and apply all migrations to set up the database schema.
- Verify that the installation was successful by running.
- This command checks for any issues with your Django project configuration.

## Next Steps

After completing the setup, proceed to [Running the Application](running.md) to start the development server.
