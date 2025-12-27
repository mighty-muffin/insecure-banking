# Testing Overview

## Introduction

The Insecure Banking application includes a comprehensive test suite that validates functionality, security vulnerabilities, and integration behavior. The test suite is organized into unit tests, integration tests, and security-focused tests.

## Testing Framework

### pytest

The application uses pytest as its primary testing framework.

**Version**: pytest >= 8.4.2

**Configuration**: `pyproject.toml`

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.test_settings"
python_paths = ["src"]
testpaths = ["tests"]
pythonpath = "src"
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

### pytest Plugins

#### pytest-django

Django integration for pytest.

**Features:**

- Django test database management
- Django settings configuration
- Fixture support for Django models
- Transaction management

#### pytest-cov

Code coverage reporting.

**Features:**

- Line coverage tracking
- Branch coverage analysis
- HTML and XML reports
- Coverage thresholds

**Coverage Threshold**: 92% minimum

#### pytest-xdist

Parallel test execution.

**Features:**

- Multi-process test execution
- Automatic core detection
- Distributed testing support

**Configuration**: `--numprocesses auto` (uses all CPU cores)

#### pytest-mock

Mocking support for pytest.

**Features:**

- mocker fixture
- Simplified mock creation
- Mock cleanup

## Test Organization

### Directory Structure

```text
tests/
├── __init__.py
├── conftest.py              # Global fixtures
├── base.py                  # Base test classes
├── database.py              # Database utilities
├── model_helpers.py         # Model test helpers
├── utils.py                 # Test utilities
├── test_integration.py      # Legacy integration tests
├── test_setup.py            # Setup validation tests
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_services.py
│   └── test_context_processors.py
├── integration/             # Integration tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth_flow.py
│   ├── test_admin_flow.py
│   ├── test_transfer_flow.py
│   └── test_database_integration.py
└── security/                # Security tests
    ├── __init__.py
    ├── conftest.py
    ├── test_sql_injection.py
    ├── test_command_injection.py
    ├── test_deserialization.py
    └── test_crypto_weaknesses.py
```

### Test Categories

Tests are organized into three main categories:

#### Unit Tests

Test individual components in isolation.

**Location**: `tests/unit/`

**Scope**:

- Model functionality
- Service methods
- Context processors
- Utility functions

**Characteristics**:

- Fast execution
- No external dependencies
- Isolated behavior testing

#### Integration Tests

Test component interactions and workflows.

**Location**: `tests/integration/`

**Scope**:

- Authentication flows
- Transfer operations
- Admin functionality
- Database operations

**Characteristics**:

- Uses test database
- Tests full request/response cycle
- Validates end-to-end behavior

#### Security Tests

Validate intentional security vulnerabilities.

**Location**: `tests/security/`

**Scope**:

- SQL injection vulnerabilities
- Command injection
- Insecure deserialization
- Weak cryptography

**Characteristics**:

- Validates exploitability
- Ensures vulnerabilities exist
- Educational demonstrations

## Test Markers

Tests can be marked with categories:

```python
@pytest.mark.unit
def test_model_creation():
    pass

@pytest.mark.integration
def test_user_login():
    pass

@pytest.mark.security
def test_sql_injection():
    pass
```

### Running Specific Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only security tests
pytest -m security
```

## Test Configuration

### Settings

Tests use dedicated settings module:

```python
DJANGO_SETTINGS_MODULE = "config.test_settings"
```

Located in `src/config/test_settings.py`

### Database

Tests use a separate test database:

- Created automatically by pytest-django
- Destroyed after test run
- Isolated from development database

### Fixtures

Global fixtures in `tests/conftest.py`:

- Database setup
- User creation
- Account creation
- Client fixtures

## Running Tests

### Run All Tests

```bash
uv run pytest
```

### Run Specific Test File

```bash
uv run pytest tests/unit/test_models.py
```

### Run Specific Test

```bash
uv run pytest tests/unit/test_models.py::test_account_creation
```

### Run with Coverage

```bash
uv run pytest --cov=src
```

### Run in Parallel

```bash
uv run pytest -n auto
```

### Verbose Output

```bash
uv run pytest -v
```

### Stop on First Failure

```bash
uv run pytest -x
```

## Code Coverage

### Coverage Requirements

Minimum coverage threshold: **92%**

### Coverage Reports

#### Terminal Output

Basic coverage summary displayed after test run.

#### HTML Report

Detailed HTML coverage report:

```bash
# Generated at: tests/coverage/html/index.html
open tests/coverage/html/index.html
```

#### XML Report

Machine-readable coverage report:

```bash
# Generated at: tests/coverage/coverage.xml
```

Used by CI/CD tools and code quality services.

### Coverage Configuration

```toml
addopts = [
    "--cov=src",                                    # Cover src directory
    "--cov-report=term-missing",                    # Show missing lines
    "--cov-report=html:tests/coverage/html",        # HTML report
    "--cov-report=xml:tests/coverage/coverage.xml", # XML report
    "--cov-fail-under=92",                          # 92% minimum
]
```

## Test Execution Flow

### Setup Phase

1. pytest collects tests
2. Test database created
3. Fixtures initialized
4. Test environment prepared

### Execution Phase

1. Tests run in parallel (if -n auto)
2. Each test gets isolated environment
3. Database transactions rolled back
4. Fixtures cleaned up

### Teardown Phase

1. Test database destroyed
2. Resources cleaned up
3. Coverage calculated
4. Reports generated

## Test Data Management

### Fixtures

Reusable test data defined in conftest.py files:

```python
@pytest.fixture
def test_user(db):
    return Account.objects.create(
        username="testuser",
        name="Test",
        surname="User",
        password="testpass"
    )
```

### Factory Pattern

Test helpers in `model_helpers.py`:

```python
def create_test_account(username="test", password="test"):
    account = Account(
        username=username,
        name="Test",
        surname="User",
        password=password
    )
    account.save()
    return account
```

## Continuous Integration

Tests run automatically in CI/CD pipeline:

```yaml
- name: Pytest - Run Unit Test
  run: |
    uv run pytest
  continue-on-error: true
```

Tests are executed on:

- Pull requests
- Main branch commits
- Tag creation

## Test Best Practices

The test suite follows these practices:

1. **Isolation**: Each test is independent
2. **Repeatability**: Tests produce same results
3. **Fast Execution**: Unit tests run quickly
4. **Clear Naming**: Test names describe behavior
5. **Single Assertion**: Tests verify one thing
6. **Fixture Usage**: Reuse common test data
7. **Database Cleanup**: Automatic transaction rollback

## Test Failures

### Debugging Failed Tests

```bash
# Show detailed output
pytest -vv

# Show stdout/stderr
pytest -s

# Show locals in tracebacks
pytest -l

# Start debugger on failure
pytest --pdb
```

### Common Failure Causes

1. Database state issues
2. Missing test data
3. Configuration errors
4. Dependency conflicts
5. Timing issues in parallel tests

## Related Documentation

- [Test Structure](structure.md)
- [Unit Tests](unit-tests.md)
- [Integration Tests](integration-tests.md)
- [Security Tests](security-tests.md)
- [Test Configuration](configuration.md)
