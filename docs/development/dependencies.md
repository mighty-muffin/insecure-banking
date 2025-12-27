# Dependency Management

## UV Package Manager

The project uses [uv](https://github.com/astral-sh/uv) an extremely fast Python package and project manager, written in Rust.

### pyproject.toml

Main project configuration:

```toml
[project]
name = "insecure-python"
version = "0.0.0"
requires-python = ">=3.10"
dependencies = [
    "asgiref==3.7.2",
    "django==4.2.4",
    "pycryptodome==3.18.0",
    "sqlparse==0.4.4",
    "typing-extensions==4.7.1",
]

[dependency-groups]
dev = [
    "pytest>=8.4.2",
    "pytest-django>=4.11.1",
    "pytest-cov>=7.0.0",
    "ruff>=0.14.4",
    "pre-commit>=4.5.0",
]
```

### uv.lock

Locked dependency versions for reproducible installs.

### requirements.txt

Generated from uv.lock for compatibility.  There is also a `pre-commit` hooks to automate this task.

```bash
uv export --frozen --output-file=requirements.txt
```

## Managing Dependencies

```bash
uv add --dev pytest # Add dev dependency
uv add django # Add to project
uv lock --upgrade # Update all
uv lock --upgrade-package django # Update specific package
uv remove package-name # Remove Dependency
uv sync --all-extras --dev --frozen # All dependencies
uv sync --frozen # Production only
uv sync --upgrade # Update dependencies
```
