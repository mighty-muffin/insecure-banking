# Code Quality Tools

## Ruff

Modern Python linter and formatter.

### Configuration

In `pyproject.toml`:
```toml
[tool.ruff]
line-length = 128
target-version = "py310"
src = ["src"]

[tool.ruff.lint]
extend-select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "UP",  # pyupgrade
    "PLR", # pylint refactor
]
```

### Usage

```bash
# Check code
uv run ruff check src/

# Fix issues
uv run ruff check --fix src/

# Format code
uv run ruff format src/
```

## Pre-commit

Git hooks for code quality.

### Setup

```bash
pre-commit install
```

### Run

```bash
# All files
pre-commit run --all-files

# Specific hook
pre-commit run ruff-check
```

## pytest

Testing framework with coverage.

### Run Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=src

# Specific marker
pytest -m unit
```

## Commitizen

Conventional commits enforcement.

### Commit Format

```text
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Testing
- chore: Maintenance

## Related Documentation

- [Pre-commit Hooks](../cicd/pre-commit.md)
- [Testing Overview](../testing/overview.md)
