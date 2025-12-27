# Development Setup

## Prerequisites

### Required Software

- **Python**: 3.10 or higher
- **uv**: Modern Python package manager
- **Git**: Version control
- **Docker**: Optional, for containerized development

### Optional Tools

- **pre-commit**: Git hooks for code quality
- **VS Code** or **PyCharm**: Recommended IDEs

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/mighty-muffin/insecure-banking.git
cd insecure-banking
```

### 2. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

### 3. Create Virtual Environment

```bash
# Create virtual environment
uv venv .venv --python 3.10

# Activate (Unix/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

### 4. Install Dependencies

```bash
# Install all dependencies including dev tools
uv sync --all-extras --dev --frozen
```

### 5. Database Setup

```bash
# Run migrations
python src/manage.py migrate

# Migrations create test data automatically
```

### 6. Install Pre-commit Hooks (Optional)

```bash
pre-commit install
```

## Verification

### Run Application

```bash
python src/manage.py runserver
```

Access at: http://localhost:8000

### Run Tests

```bash
uv run pytest
```

### Check Code Quality

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Run linter
uv run ruff check src/

# Run formatter
uv run ruff format src/
```

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Ruff
- Pylance
- Django

Settings:
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "ruff"
}
```

### PyCharm

1. Open project
2. Set Python interpreter to `.venv/bin/python`
3. Enable Django support
4. Configure ruff as external tool

## Environment Variables

Create `.env` file (optional):

```env
DEBUG=True
SECRET_KEY=django-insecure-development-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Common Issues

### uv not found

Ensure uv is in PATH:
```bash
export PATH="$HOME/.cargo/bin:$PATH"
```

### Permission denied

Fix permissions:
```bash
chmod +x install/*
```

### Database errors

Reset database:
```bash
rm src/db.sqlite3
python src/manage.py migrate
```

## Next Steps

- [Running the Application](running.md)
- [Docker Containerization](docker.md)
- [Contributing Guidelines](contributing.md)
