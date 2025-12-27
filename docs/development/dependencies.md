# Dependency Management

## UV Package Manager

The project uses uv for modern, fast Python dependency management.

## Configuration Files

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

Generated from uv.lock for compatibility:
```bash
uv export --frozen --output-file=requirements.txt
```

## Managing Dependencies

### Install Dependencies

```bash
# All dependencies
uv sync --all-extras --dev --frozen

# Production only
uv sync --frozen

# Update dependencies
uv sync --upgrade
```

### Add Dependency

```bash
# Add to project
uv add django

# Add dev dependency
uv add --dev pytest
```

### Remove Dependency

```bash
uv remove package-name
```

### Update Dependencies

```bash
# Update all
uv lock --upgrade

# Update specific package
uv lock --upgrade-package django
```

## Production Dependencies

- **django**: Web framework
- **pycryptodome**: Cryptography (for demos)
- **asgiref**: ASGI utilities
- **sqlparse**: SQL parsing
- **typing-extensions**: Type hints

## Development Dependencies

- **pytest**: Testing framework
- **pytest-django**: Django integration
- **pytest-cov**: Code coverage
- **pytest-xdist**: Parallel testing
- **pytest-mock**: Mocking
- **ruff**: Linting and formatting
- **pre-commit**: Git hooks

## Dependency Security

### Vulnerability Scanning

```bash
# Using safety (if installed)
pip install safety
safety check

# Using GitHub Dependabot
# Automatic in repository
```

### Update Strategy

- Regular updates for security patches
- Test thoroughly before updating major versions
- Use `uv.lock` for reproducible builds

## Cache Management

```bash
# View cache
uv cache dir

# Clean cache
uv cache clean

# Prune cache (CI)
uv cache prune --ci
```

## Related Documentation

- [Development Setup](setup.md)
- [Testing Configuration](../testing/configuration.md)
