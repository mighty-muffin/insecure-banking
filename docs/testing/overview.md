---
hide:
  - toc
---

# Testing Overview

The project includes a comprehensive test suite organized by test type:

```bash
tests/
├── e2e/               # End-to-end tests using Playwright
├── integration/       # Integration tests for component interactions
├── security/          # Security vulnerability tests
└── unit/              # Unit tests for individual components
```

This project use [pytest-xdist](https://github.com/pytest-dev/pytest-xdist); a pytest plugin for distributed testing and loop-on-failures testing modes.  `pytest-xdist` shards your test suite on all available CPU core for faster performances.  Sometimes it can generates flaky test but its pretty rare.  Just re-run the test and you are good.

## Running Tests

Execute the complete test suite:

```bash
uv run pytest                               # Run the whole test suite
uv run pytest tests/unit/test_models.py     # Run a single test file
uv run pytest --cov=src --cov-report=html   # Generate code coverage reports
```

Run tests by category:

```bash
uv run pytest -m e2e              # End-to-end tests only
uv run pytest -m integration      # Integration tests only
uv run pytest -m security         # Security tests only
uv run pytest -m unit             # Unit tests only
```

## Test Categories

<!-- TODO : Improve this section -->

**Unit Tests** validate individual functions and methods in isolation:

- test_context_processors.py: Tests for template context processors
- test_models.py: Tests for database models
- test_services.py: Tests for service layer functions
- test_views.py: Tests for view functions

**Integration Tests** validate interactions between components:

- test_admin_flow.py: Administrative function tests
- test_auth_flow.py: Authentication workflow tests
- test_database_integration.py: Database operation tests
- test_transfer_flow.py: Transfer process tests

**End-to-end tests** use Playwright to simulate user interactions:

- test_activity.py: Activity viewing tests
- test_login.py: Login functionality tests
- test_logout.py: Logout functionality tests
- test_transfer.py: Transfer workflow tests

**Security tests** validate the presence of intentional vulnerabilities:

- test_command_injection.py: Command injection tests
- test_crypto_weaknesses.py: Cryptographic weakness tests
- test_deserialization.py: Unsafe deserialization tests
- test_sql_injection.py: SQL injection vulnerability tests
