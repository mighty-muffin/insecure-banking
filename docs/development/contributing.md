# Contributing Guide

Before contributing, ensure you have completed the [Development Setup](setup.md) and can successfully run the application locally.

## Development Workflow

1. Create a working Branch

   ```bash
   git checkout -b feature/your-feature-name
   code .
   ```

2. Code Quality Checks

   ```bash
   uv run pytest # Ensure all tests pass and code coverage is maintained (92%+)
   pre-commit run --all-files # Run code quality checks using pre-commit
   ```

3. Commit Changes

   ```bash
   git add .
   git commit -m "feat: add new transfer validation" # Write clear, descriptive commit messages
   git push
   ```

## Coding Standards

### Conventional Commits

- Use descriptive branch names:
  - `feature/` for new features
  - `bugfix/` for bug fixes
  - `docs/` for documentation changes
  - `refactor/` for code refactoring

- Use conventional commit prefixes:
  - `<type>(bump):` for any breakage (trigger major release)
  - `feat:` for new features (trigger minor release)
  - `fix:` for bug fixes (trigger patch release)
  - `chore:` for maintenance tasks
  - `docs:` for documentation
  - `refactor:` for code refactoring
  - `test:` for test additions or changes

### Python Style Guide

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Maximum line length: 120 characters
- Use descriptive variable and function names

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
