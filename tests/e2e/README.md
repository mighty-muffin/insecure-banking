# End-to-End Testing with Playwright

This directory contains Playwright-based end-to-end tests for the insecure banking application.

## Prerequisites

- Python 3.10+
- Playwright and pytest-playwright installed
- The application running on http://localhost:8000

## Installation

Install the required dependencies:

```bash
# Install Python dependencies
pip install playwright pytest-playwright

# Install Playwright browsers
playwright install chromium
```

If using `uv` (the project's package manager):

```bash
uv sync --all-extras --dev
playwright install chromium
```

## Running the Tests

### Start the Application

First, ensure the application is running:

```bash
python src/manage.py migrate
python src/manage.py runserver
```

The application should be accessible at http://localhost:8000.

### Run E2E Tests

In a separate terminal, run the e2e tests:

```bash
# Run all e2e tests (disable Django plugin since e2e tests use live app)
pytest tests/e2e/ -p no:django -m e2e --no-cov

# Run specific test file
pytest tests/e2e/test_auth_flow.py -p no:django -m e2e --no-cov

# Run with headed browser (see what's happening)
pytest tests/e2e/ -p no:django -m e2e --no-cov --headed

# Run with slow motion (easier to debug)
pytest tests/e2e/ -p no:django -m e2e --no-cov --headed --slowmo 1000

# Run specific test
pytest tests/e2e/test_auth_flow.py::test_successful_login_and_logout -p no:django -m e2e --no-cov

# Run without parallel execution (easier to debug)
pytest tests/e2e/ -p no:django -m e2e --no-cov -n0
```

### Important Notes

- **Always use `-p no:django` flag** when running e2e tests to disable pytest-django plugin
- **Always use `--no-cov` flag** to disable code coverage for e2e tests
- E2E tests interact with the live application running on port 8000
- E2E tests do not use the Django test database - they use the actual application database

### Run Only E2E Tests (Exclude Other Tests)

```bash
pytest -p no:django -m e2e --no-cov
```

### Run All Tests Except E2E

```bash
pytest -m "not e2e"
```

## Test Structure

- `conftest.py` - Pytest fixtures and configuration for Playwright
- `test_auth_flow.py` - Authentication and login/logout tests
- `test_dashboard.py` - Dashboard and navigation tests
- `test_transfer_flow.py` - Money transfer functionality tests

## Test Credentials

The tests use the default application credentials:
- Username: `john`
- Password: `test`

Make sure this user exists in the application database before running tests.

## Debugging Tests

### Visual Debugging

Run tests with headed browser to see what's happening:

```bash
pytest tests/e2e/ -p no:django -m e2e --no-cov --headed --slowmo 500
```

### Screenshots on Failure

Playwright automatically captures screenshots on test failure. They are saved in the `test-results` directory.

### Trace Viewing

You can enable tracing for detailed debugging:

```bash
pytest tests/e2e/ -p no:django -m e2e --no-cov --tracing on
```

Then view the trace:

```bash
playwright show-trace test-results/<test-name>/trace.zip
```

## Continuous Integration

To run e2e tests in CI, ensure:

1. The application is started in the background
2. Chromium is installed (`playwright install --with-deps chromium`)
3. Tests are run with headless mode (default)
4. Django plugin is disabled with `-p no:django`
5. Coverage is disabled with `--no-cov`

Example CI workflow:

```yaml
- name: Install dependencies
  run: |
    pip install -r requirements.txt
    pip install playwright pytest-playwright
    playwright install --with-deps chromium

- name: Run migrations
  run: python src/manage.py migrate

- name: Start server
  run: python src/manage.py runserver &
  
- name: Wait for server
  run: sleep 5

- name: Run E2E tests
  run: pytest tests/e2e/ -p no:django -m e2e --no-cov
```

## Writing New Tests

When writing new e2e tests:

1. Use the `@pytest.mark.e2e` decorator
2. Use the provided fixtures (`page`, `logged_in_page`, `base_url`)
3. Follow existing test patterns
4. Use Playwright's `expect` API for assertions
5. Add appropriate waits for dynamic content
6. Consider element visibility - some elements may be in dropdowns or hidden menus

Example:

```python
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
def test_my_feature(logged_in_page: Page, base_url: str):
    """Test description."""
    page = logged_in_page
    
    # Navigate
    page.goto(f"{base_url}/my-feature")
    
    # Interact
    page.click('button#my-button')
    
    # Assert
    expect(page.locator('#result')).to_contain_text('Success')
```

## Notes

- These tests are designed for the intentionally vulnerable banking application
- Some security vulnerabilities are preserved by design
- Tests focus on functionality, not security validation
- The application runs on port 8000 by default
- Some tests may fail if elements are not visible (dropdown menus, etc.) - these are known limitations
