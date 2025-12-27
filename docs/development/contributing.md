# Contributing Guidelines

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make changes
5. Run tests
6. Submit pull request

## Development Workflow

### Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### Make Changes

Follow code style guidelines:
- Use ruff for formatting
- Write tests for new code
- Update documentation

### Run Quality Checks

```bash
# Format code
uv run ruff format src/

# Run linter
uv run ruff check src/ --fix

# Run tests
uv run pytest

# Run pre-commit
pre-commit run --all-files
```

### Commit Changes

Use conventional commits:
```bash
git commit -m "feat(transfer): add transfer validation"
```

### Push and Create PR

```bash
git push origin feature/your-feature-name
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

## Pull Request Process

1. Ensure tests pass
2. Update documentation
3. Add changelog entry
4. Request review
5. Address feedback
6. Merge when approved

## Questions

Open an issue for:
- Bug reports
- Feature requests
- Documentation improvements
- Questions

## Related Documentation

- [Development Setup](setup.md)
- [Testing Overview](../testing/overview.md)
- [Code Quality Tools](code-quality.md)
