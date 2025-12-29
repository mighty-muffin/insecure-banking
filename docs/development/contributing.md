# Contributing Guide

Before contributing, ensure you have completed the [Development Setup](setup.md) and can successfully run the application locally.

## Development Workflow

### 1. Create a Feature Branch

Create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names:

- `feature/` for new features
- `bugfix/` for bug fixes
- `docs/` for documentation changes
- `refactor/` for code refactoring

### 2. Make Changes

Make your changes following the coding standards outlined below.

### 3. Run Tests

Ensure all tests pass before committing:

```bash
pytest
```

Run specific test suites:

```bash
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/security/      # Security tests only
pytest tests/e2e/          # End-to-end tests only
```

### 4. Code Quality Checks

Run code quality checks using pre-commit:

```bash
pre-commit run --all-files
```

This will run:

- Ruff for linting and formatting
- Bandit for security checks
- Other configured hooks

### 5. Commit Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add new transfer validation"
```

Use conventional commit prefixes:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for test additions or changes
- `refactor:` for code refactoring
- `chore:` for maintenance tasks

### 6. Push and Create Pull Request

Push your branch and create a pull request:

```bash
git push origin feature/your-feature-name
```

## Coding Standards

### Python Style Guide

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Maximum line length: 120 characters
- Use descriptive variable and function names

### Django Conventions

- Follow Django best practices for models, views, and templates
- Use Django ORM for database operations
- Implement proper error handling
- Add docstrings to functions and classes

### Testing Requirements

- Write unit tests for new functions and methods
- Add integration tests for new features
- Maintain or improve code coverage
- Test edge cases and error conditions

## Code Review Process

All contributions must go through code review:

1. Create a pull request with a clear description
2. Ensure all CI/CD checks pass
3. Address reviewer feedback
4. Obtain approval from at least one maintainer

## Documentation

Update documentation when:

- Adding new features
- Changing existing behavior
- Modifying setup or deployment processes
- Adding new dependencies

## Dependency Management

When adding new dependencies:

1. Add the dependency to `pyproject.toml`
2. Run `uv sync` to update lockfiles
3. Document the reason for the dependency
4. Ensure the dependency does not introduce security vulnerabilities

## Questions and Support

If you have questions or need support:

- Review existing documentation
- Check closed issues and pull requests
- Open a new issue for discussion

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project.
