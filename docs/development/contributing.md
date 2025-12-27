# Contributing Guidelines

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make changes
5. Run tests
6. Submit pull request

## Development Workflow

Follow code style guidelines:

- Use ruff for formatting
- Write tests for new code
- Update documentation

```bash
# Use conventional commits
git checkout -b <type>/<your-changes>
```

### Run Quality Checks

```bash
# Format code
uv run ruff format src/
# Run linter
uv run ruff check src/ --fix
# Run tests
uv run pytest
# Run pre-commit
pre-commit install --allow-missing-config
pre-commit run --all-files
```

Then create pull request on GitHub.

## Code Standards

### Python Style

- Follow PEP 8
- Line length: 128 characters
- Use type hints
- Document functions

### Testing

- Write tests for new features
- Maintain 92% coverage
- Use descriptive test names

### Documentation

- Update relevant docs
- Add docstrings
- Keep README current
