# Test Configuration

## pytest Configuration

The test configuration is defined in `pyproject.toml` under the `[tool.pytest.ini_options]` section.

### Basic Configuration

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.test_settings"
python_paths = ["src"]
testpaths = ["tests"]
pythonpath = "src"
```

#### Settings Module

```python
DJANGO_SETTINGS_MODULE = "config.test_settings"
```

Specifies Django settings module for tests, located at `src/config/test_settings.py`.

#### Python Paths

```python
python_paths = ["src"]
pythonpath = "src"
```

Adds `src` directory to Python path for imports.

#### Test Paths

```python
testpaths = ["tests"]
```

Tells pytest where to find tests.

### Test Execution Options

```toml
addopts = [
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html:tests/coverage/html",
    "--cov-report=xml:tests/coverage/coverage.xml",
    "--cov-fail-under=92",
    "--numprocesses", "auto",
    "--strict-markers",
    "--tb=short",
    "--verbose",
]
```

#### Coverage Options

- `--cov=src`: Measure coverage for src directory
- `--cov-report=term-missing`: Show missing lines in terminal
- `--cov-report=html:tests/coverage/html`: Generate HTML report
- `--cov-report=xml:tests/coverage/coverage.xml`: Generate XML report
- `--cov-fail-under=92`: Fail if coverage below 92%

#### Execution Options

- `--numprocesses auto`: Run tests in parallel using all CPU cores
- `--strict-markers`: Enforce marker registration
- `--tb=short`: Short traceback format
- `--verbose`: Verbose output

### Test Markers

```toml
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "security: Security-focused tests",
]
```

Defines custom markers for categorizing tests.

Usage:

```bash
pytest -m unit        # Run unit tests
pytest -m integration # Run integration tests
pytest -m security    # Run security tests
```

### Filter Warnings

```toml
filterwarnings = [
    "ignore::django.utils.deprecation.RemovedInDjango50Warning",
    "ignore::DeprecationWarning",
]
```

Suppresses specific warning categories during test execution.

## Django Test Settings

Test-specific Django configuration in `src/config/test_settings.py`:

### Database Configuration

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # In-memory database for tests
    }
}
```

Uses in-memory SQLite database for faster test execution.

### Test-Specific Settings

```python
# Disable migrations for faster tests
MIGRATION_MODULES = {
    'web': None,
}

# Use faster password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
```

### Debug Mode

```python
DEBUG = True  # Enable for detailed error messages
```

## Coverage Configuration

### Coverage Settings

Coverage measurement configured via pytest options in `pyproject.toml`.

### Coverage Reports

Three report formats generated:

1. **Terminal**: Displayed after test run
2. **HTML**: `tests/coverage/html/index.html`
3. **XML**: `tests/coverage/coverage.xml`

### Coverage Threshold

```toml
--cov-fail-under=92
```

Tests fail if coverage drops below 92%.

### Coverage Exclusions

Can be configured in `.coveragerc` or `pyproject.toml`:

```toml
[tool.coverage.run]
omit = [
    "*/tests/*",
    "*/migrations/*",
]
```

## Parallel Execution

### Configuration

```toml
--numprocesses auto
```

Automatically uses all available CPU cores.

### Benefits

- Faster test execution
- Efficient resource usage
- Scales with hardware

### Considerations

- Tests must be independent
- No shared state between tests
- Database isolation required

## Environment Variables

Tests can use environment variables:

```bash
# Set environment variable
export TEST_DATABASE=test_db

# Run tests
pytest
```

Access in tests:

```python
import os
test_db = os.getenv('TEST_DATABASE', 'default')
```

## Fixtures

Global fixtures in `tests/conftest.py`:

```python
@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Custom database setup"""
    with django_db_blocker.unblock():
        # Setup code
        pass
```

## Test Database Management

### Creation

pytest-django creates test database automatically.

### Cleanup

Test database destroyed after test session.

### Persistence

For debugging, can keep database:

```bash
pytest --reuse-db
```

## Command Line Options

### Common Options

```bash
# Verbose output
pytest -v

# Very verbose
pytest -vv

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Run specific marker
pytest -m unit

# Run specific test
pytest tests/unit/test_models.py::test_account_creation

# Show slow tests
pytest --durations=10

# Generate HTML report
pytest --html=report.html
```

## CI/CD Configuration

In GitHub Actions workflow:

```yaml
- name: Pytest - Run Unit Test
  run: |
    uv run pytest
  continue-on-error: true
```

Continues on test failure to allow review of results.

## Related Documentation

- [Testing Overview](overview.md)
- [Test Structure](structure.md)
- [Unit Tests](unit-tests.md)
- [Integration Tests](integration-tests.md)
- [Security Tests](security-tests.md)
