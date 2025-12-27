# Pre-commit Hooks

## Overview

Pre-commit hooks enforce code quality and consistency before commits. Configured in `.pre-commit-config.yaml`.

## Configuration

```yaml
default_language_version:
  python: python3.10

default_stages:
  - pre-commit

default_install_hook_types:
  - commit-msg
  - pre-commit
```

## Hooks

### Commit Message Validation

```yaml
- repo: https://github.com/commitizen-tools/commitizen
  hooks:
    - id: commitizen
      stages: [commit-msg]
```

Validates commit messages follow conventional commits format.

### General Checks

- Block large files (> 2MB)
- Check JSON syntax
- Fix end-of-file issues
- Fix mixed line endings
- Remove trailing whitespace
- Pretty format JSON files

### Markdown Linting

```yaml
- repo: https://github.com/igorshubovych/markdownlint-cli
  hooks:
    - id: markdownlint
      args: [--config, .config/.markdown-lint.yml]
```

### YAML Linting

```yaml
- repo: https://github.com/adrienverge/yamllint
  hooks:
    - id: yamllint
      args: [-c, .config/.yaml-lint.yml]
```

### Python: UV Export

```yaml
- repo: https://github.com/astral-sh/uv-pre-commit
  hooks:
    - id: uv-export
```

Exports dependencies to requirements.txt.

### Python: Ruff

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  hooks:
    - id: ruff-check
      args: [--fix]
      stages: [manual]
    - id: ruff-format
      stages: [manual]
```

Python linting and formatting (manual stage).

### Python: Pytest

```yaml
- repo: local
  hooks:
    - id: pytest
      entry: uv run pytest
      language: system
      pass_filenames: false
```

Runs tests on commit.

### GitHub Actions Security

```yaml
- repo: local
  hooks:
    - id: pin-github-action
      entry: "pin-github-action ."
      language: node
      stages: [manual]
```

Pins GitHub Actions to commit SHAs (manual).

## Installation

```bash
# Install hooks
pre-commit install

# Install all hook types
pre-commit install --install-hooks
```

## Running Hooks

```bash
# Run all hooks
pre-commit run --all-files

# Run specific hook
pre-commit run pytest

# Skip hooks
git commit --no-verify
```

## Stages

- **pre-commit**: Before commit
- **commit-msg**: Validate commit message
- **manual**: Run manually only

## Related Documentation

- [CI/CD Overview](overview.md)
- [Code Quality Tools](../development/code-quality.md)
