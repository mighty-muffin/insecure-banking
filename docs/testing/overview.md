# Testing Overview

## Test Structure

The project includes a comprehensive test suite organized by test type:

```bash
tests/
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests for component interactions
├── security/          # Security vulnerability tests
└── e2e/              # End-to-end tests using Playwright
```

## Running Tests

### Run All Tests

Execute the complete test suite:

```bash
pytest
```

### Run Specific Test Suites

Run tests by category:

```bash
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests only
pytest tests/security/          # Security tests only
pytest tests/e2e/              # End-to-end tests only
```

### Run Specific Test Files

Run a single test file:

```bash
pytest tests/unit/test_models.py
```

### Run Tests with Coverage

Generate code coverage reports:

```bash
pytest --cov=src --cov-report=html
```

View the coverage report by opening `tests/coverage/html/index.html` in a browser.

## Test Categories

### Unit Tests

Unit tests validate individual functions and methods in isolation:

- **test_models.py**: Tests for database models
- **test_services.py**: Tests for service layer functions
- **test_views.py**: Tests for view functions
- **test_context_processors.py**: Tests for template context processors

Unit tests use mocking to isolate components and run quickly.

### Integration Tests

Integration tests validate interactions between components:

- **test_auth_flow.py**: Authentication workflow tests
- **test_transfer_flow.py**: Transfer process tests
- **test_admin_flow.py**: Administrative function tests
- **test_database_integration.py**: Database operation tests

Integration tests use a test database and validate complete workflows.

### Security Tests

Security tests validate the presence of intentional vulnerabilities:

- **test_sql_injection.py**: SQL injection vulnerability tests
- **test_command_injection.py**: Command injection tests
- **test_crypto_weaknesses.py**: Cryptographic weakness tests
- **test_deserialization.py**: Unsafe deserialization tests

These tests ensure vulnerabilities remain present for educational purposes.

### End-to-End Tests

End-to-end tests use Playwright to simulate user interactions:

- **test_login.py**: Login functionality tests
- **test_transfer.py**: Transfer workflow tests
- **test_activity.py**: Activity viewing tests
- **test_logout.py**: Logout functionality tests

E2E tests require the application to be running and validate the complete user experience.

## Test Configuration

### conftest.py

Each test directory contains a `conftest.py` file with pytest fixtures and configuration.

### Test Settings

Test-specific Django settings are defined in `src/config/test_settings.py`.

### Test Database

Integration and unit tests use a separate test database that is created and destroyed for each test run.

## Writing Tests

### Unit Test Example

```python
def test_account_balance(test_account):
    """Test account balance calculation."""
    assert test_account.balance >= 0
    assert isinstance(test_account.balance, float)
```

### Integration Test Example

```python
def test_transfer_between_accounts(client, test_user):
    """Test money transfer between accounts."""
    client.login(username=test_user.username, password="password")
    response = client.post("/transfer", data={
        "from_account": 1,
        "to_account": 2,
        "amount": 100.0
    })
    assert response.status_code == 200
```

## Best Practices

### Test Isolation

Each test should be independent and not rely on other tests.

### Use Fixtures

Use pytest fixtures for common test data and setup.

### Descriptive Names

Use descriptive test function names that explain what is being tested.

### Assert Clearly

Write clear assertions with helpful error messages.

### Test Edge Cases

Test boundary conditions and error scenarios, not just happy paths.

## Continuous Integration

Tests are automatically run in CI/CD pipelines on:

- Pull request creation
- Commits to main branch
- Tag creation

All tests must pass before code can be merged.
