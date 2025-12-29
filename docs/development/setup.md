# Development Setup

## Prerequisites

Before setting up the development environment, ensure you have the following installed:

- Python 3.10 or higher
- Git
- uv (Python package installer and resolver)

## Installing uv

If you do not have `uv` installed, install it using the official installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For other installation methods, refer to the [uv documentation](https://docs.astral.sh/uv/).

## Repository Setup

Clone the repository and navigate to the project directory:

```bash
git clone <repository-url>
cd insecure-banking
```

## Virtual Environment

Create and activate a virtual environment using uv:

```bash
uv venv .venv --python 3.10
source .venv/bin/activate  # On Linux/macOS
# or
.venv\Scripts\activate  # On Windows
```

## Installing Dependencies

Install all project dependencies including development dependencies:

```bash
uv sync --all-extras --dev --frozen
```

This command will:

- Install all production dependencies
- Install development dependencies (testing, linting, etc.)
- Install documentation dependencies (mkdocs, mkdocs-material)
- Lock dependencies to ensure reproducible builds

## Database Setup

Initialize the database with migrations:

```bash
python manage.py migrate
```

This will create the SQLite database file (`db.sqlite3`) and apply all migrations to set up the database schema.

## Verifying the Setup

Verify that the installation was successful by running:

```bash
python manage.py check
```

This command checks for any issues with your Django project configuration.

## IDE Configuration

### VS Code

If you are using Visual Studio Code, ensure the Python extension is installed. The workspace will automatically detect the virtual environment in `.venv`.

### PyCharm

For PyCharm users, configure the project interpreter to use the virtual environment at `.venv/bin/python`.

## Next Steps

After completing the setup, proceed to [Running the Application](running.md) to start the development server.
