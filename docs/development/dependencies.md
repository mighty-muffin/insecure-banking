# Dependency Management

## Overview

This project uses `uv` for Python package management and dependency resolution. Dependencies are defined in `pyproject.toml` and locked in `uv.lock`.

## Dependency Files

### pyproject.toml

The `pyproject.toml` file defines project metadata and dependencies:

- **project.dependencies**: Production dependencies
- **dependency-groups.dev**: Development dependencies
- **dependency-groups.docs**: Documentation dependencies

### uv.lock

The `uv.lock` file contains locked versions of all dependencies and their transitive dependencies, ensuring reproducible installations.

### requirements.txt

The `requirements.txt` file is generated from `uv.lock` and contains only production dependencies for deployment.

## Managing Dependencies

### Installing Dependencies

Install all dependencies including development and documentation tools:

```bash
uv sync --all-extras --dev --frozen
```

Install only production dependencies:

```bash
uv sync --frozen
```

### Adding New Dependencies

Add a production dependency:

```bash
uv add package-name
```

Add a development dependency:

```bash
uv add --dev package-name
```

Specify a version constraint:

```bash
uv add "package-name>=1.0.0,<2.0.0"
```

### Updating Dependencies

Update all dependencies:

```bash
uv sync --upgrade
```

Update a specific package:

```bash
uv add --upgrade package-name
```

### Removing Dependencies

Remove a dependency:

```bash
uv remove package-name
```

### Exporting Requirements

Export production dependencies to requirements.txt:

```bash
uv export --no-dev --output-file requirements.txt
```

## Key Dependencies

### Production Dependencies

- **Django 4.2.4**: Web framework
- **pycryptodome 3.18.0**: Cryptographic operations
- **PyYAML 5.3.1**: YAML parsing
- **sqlparse 0.4.2**: SQL parsing utilities

### Development Dependencies

- **pytest**: Testing framework
- **pytest-django**: Django testing support
- **pytest-cov**: Coverage reporting
- **pytest-playwright**: Browser automation for E2E tests
- **ruff**: Fast Python linter and formatter
- **bandit**: Security linter
- **pre-commit**: Git hooks for code quality

### Documentation Dependencies

- **mkdocs**: Documentation site generator
- **mkdocs-material**: Material theme for mkdocs

## Dependency Security

### Checking for Vulnerabilities

Check dependencies for known security vulnerabilities using available security tools.

### Keeping Dependencies Updated

Regularly update dependencies to receive security patches:

1. Review changelogs for breaking changes
2. Run `uv sync --upgrade`
3. Run the test suite to verify compatibility
4. Commit the updated lockfile

## Best Practices

### Pin Major Versions

Use version constraints to prevent breaking changes:

```toml
dependencies = [
    "django>=4.2.0,<5.0.0",
]
```

### Separate Development Dependencies

Keep development dependencies separate from production dependencies to minimize deployment size.

### Lock Dependencies

Always commit `uv.lock` to ensure all team members use identical dependency versions.

### Regular Updates

Schedule regular dependency updates to stay current with security patches.

## Troubleshooting

### Dependency Conflicts

If you encounter dependency conflicts:

1. Review the error message to identify conflicting packages
2. Check if version constraints are too restrictive
3. Consider updating conflicting packages together

### Lock File Out of Sync

If the lock file is out of sync with `pyproject.toml`:

```bash
uv sync
```

### Cache Issues

Clear the uv cache if experiencing persistent issues:

```bash
uv cache clean
```
