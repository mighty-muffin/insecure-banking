---
hide:
  - toc
---
# Code Quality

Code quality is the measure of how reliable, efficient, readable, and maintainable software code is, encompassing its ability to function correctly, be understood, modified, and extended easily by developers while meeting user needs and security standards. It's about more than just being bug-free; high-quality code is well-structured, performant, testable, and adheres to best practices, making it a valuable asset rather than a liability.

## Pre-Commit

[pre-commit](https://github.com/pre-commit/pre-commit); a framework for managing and maintaining multi-language pre-commit hooks.
[prek](https://github.com/j178/prek); alternatively a better `pre-commit`, re-engineered in Rust.

```bash
pre-commit install --allow-missing-config
pre-commit autoupdate # Update hooks
pre-commit run --all-files # All files
pre-commit run ruff-check # Specific hook
```

> **_NOTE:_**  Pre-commit hooks run all check automatically when enable properly.

## Pytest

The [pytest](https://github.com/pytest-dev/pytest) framework makes it easy to write small tests, yet scales to support complex functional testing.
Couple of add-on are installed (pytest-cov, pytest-django, pytest-mock, pytest-xdist) to improve the experience.
There is a minimal sets of e2e test using [playwright](https://playwright.dev/) that is available.

```bash
uv run playwright install --with-deps # Install additional playwright dependencies
uv run pytest # All tests
uv run pytest --cov=src # With coverage
uv run pytest -m unit # Specific marker
```

## Ruff

[ruff](https://github.com/astral-sh/ruff); an extremely fast Python linter and code formatter, written in Rust.

```bash
uv run ruff check src/ # Check code
uv run ruff check --fix # Fix issues
uv run ruff format # Format code
```

> **_ERROR:_**  `ruff` is not really implemented yet so.. do not run it

## Ty

[ty](https://github.com/astral-sh/ty); an extremely fast Python type checker and language server, written in Rust.

```bash
uv run ty check src/ # Check code
```

> **_ERROR:_**  `ty` is not really implemented yet so.. do not run it

## Code Style Guidelines

### Python Formatting

- Maximum line length: 120 characters
- Use double quotes for strings
- Add trailing commas in multi-line data structures
- Follow PEP 8 conventions

### Docstrings

Use docstrings for:

- Modules
- Classes
- Public functions and methods

Follow Google or NumPy docstring style conventions.

## CI/CD Integration

Code quality checks run automatically in CI/CD pipelines:

- On pull request creation
- On commits to main branch
- Before deployment

All checks must pass before code can be merged.
