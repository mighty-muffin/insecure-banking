# Test Structure

## Overview

The test suite is organized into a clear hierarchy with shared fixtures, utilities, and base classes to promote code reuse and maintainability.

## Root Test Directory

### tests/__init__.py

Marks the tests directory as a Python package.

### tests/conftest.py

Global pytest configuration and fixtures available to all tests.

**Key Fixtures:**

```python
@pytest.fixture
def test_db(db):
    """Provides access to test database"""
    pass

@pytest.fixture
def django_client(client):
    """Provides Django test client"""
    return client

@pytest.fixture
def test_user(db):
    """Creates a test user account"""
    from web.models import Account
    account = Account(
        username="testuser",
        name="Test",
        surname="User",
        password="testpass"
    )
    account.save()
    return account
```

### tests/base.py

Base test classes providing common functionality.

```python
class BaseTest:
    """Base class for all tests"""
    pass

class BaseDatabaseTest(BaseTest):
    """Base class for tests requiring database access"""
    pass
```

### tests/database.py

Database utility functions for tests.

**Functions:**

- Database setup helpers
- Data seeding utilities
- Query execution helpers
- Test data cleanup

### tests/model_helpers.py

Helper functions for creating model instances in tests.

**Functions:**

```python
def create_test_account(username="test", password="test")
def create_test_cash_account(username, number, balance=1000.0)
def create_test_credit_account(cash_account_id, number, username)
def create_test_transfer(from_account, to_account, amount=100.0)
def create_test_transaction(number, description, amount, balance)
```

### tests/utils.py

General test utility functions.

**Functions:**

- String manipulation helpers
- Data validation utilities
- Test assertion helpers
- Mock data generators

## Unit Tests Directory

### tests/unit/conftest.py

Unit test-specific fixtures.

```python
@pytest.fixture
def mock_service(mocker):
    """Provides mocked service"""
    pass
```

### tests/unit/test_models.py

Tests for Django models.

**Test Coverage:**

- Model field definitions
- Model validation
- Model serialization (as_dict/from_dict)
- Model relationships
- Model constraints

**Example Tests:**

```python
def test_account_creation(db):
    """Test Account model creation"""
    
def test_transfer_serialization(db):
    """Test Transfer model serialization"""
    
def test_cashaccount_fields(db):
    """Test CashAccount field definitions"""
```

### tests/unit/test_services.py

Tests for service layer methods.

**Test Coverage:**

- AccountService authentication
- CashAccountService queries
- CreditAccountService operations
- ActivityService data retrieval
- TransferService transaction processing
- StorageService file operations

**Example Tests:**

```python
def test_account_service_find_by_username(db):
    """Test finding accounts by username"""
    
def test_cash_account_service_get_balance(db):
    """Test balance retrieval"""
    
def test_transfer_service_create_transfer(db):
    """Test transfer creation"""
```

### tests/unit/test_context_processors.py

Tests for Django context processors.

**Test Coverage:**

- version_info context processor
- Template context data

**Example Tests:**

```python
def test_version_info_processor():
    """Test version info added to context"""
```

## Integration Tests Directory

### tests/integration/conftest.py

Integration test-specific fixtures.

```python
@pytest.fixture
def authenticated_client(client, test_user):
    """Provides authenticated test client"""
    client.login(username=test_user.username, password="testpass")
    return client
```

### tests/integration/test_auth_flow.py

Tests for authentication and authorization flows.

**Test Coverage:**

- User login success
- User login failure
- User logout
- Session management
- Authentication middleware
- Redirect behavior

**Example Tests:**

```python
def test_successful_login(client, test_user):
    """Test successful user login"""
    
def test_failed_login(client):
    """Test failed login attempt"""
    
def test_logout_redirect(authenticated_client):
    """Test logout redirects to login"""
    
def test_unauthenticated_redirect(client):
    """Test unauthenticated user redirected"""
```

### tests/integration/test_admin_flow.py

Tests for admin functionality.

**Test Coverage:**

- Admin dashboard access
- User list display
- Admin permissions (or lack thereof)

**Example Tests:**

```python
def test_admin_view_access(authenticated_client):
    """Test accessing admin view"""
    
def test_admin_view_displays_users(authenticated_client):
    """Test admin view shows all users"""
```

### tests/integration/test_transfer_flow.py

Tests for money transfer operations.

**Test Coverage:**

- Transfer form display
- Transfer submission
- Transfer confirmation
- Transfer completion
- Balance updates
- Transaction recording
- Error handling

**Example Tests:**

```python
def test_transfer_form_display(authenticated_client):
    """Test transfer form loads"""
    
def test_transfer_submission(authenticated_client):
    """Test submitting transfer"""
    
def test_transfer_updates_balances(authenticated_client, db):
    """Test transfer updates account balances"""
```

### tests/integration/test_database_integration.py

Tests for database operations and integrity.

**Test Coverage:**

- Model CRUD operations
- Transaction management
- Database constraints
- Query execution

**Example Tests:**

```python
def test_account_crud_operations(db):
    """Test creating, reading, updating, deleting accounts"""
    
def test_transfer_transaction_rollback(db):
    """Test transaction rollback on error"""
```

## Security Tests Directory

### tests/security/conftest.py

Security test-specific fixtures and utilities.

```python
@pytest.fixture
def sql_injection_payloads():
    """Provides common SQL injection payloads"""
    return [
        "' OR '1'='1",
        "'; DROP TABLE web_account; --",
        "admin' --",
    ]
```

### tests/security/test_sql_injection.py

Tests validating SQL injection vulnerabilities.

**Test Coverage:**

- Authentication bypass
- Data extraction
- Query manipulation
- Multiple injection points

**Example Tests:**

```python
def test_authentication_sql_injection(client):
    """Test SQL injection in authentication"""
    
def test_account_query_sql_injection(authenticated_client):
    """Test SQL injection in account queries"""
```

### tests/security/test_command_injection.py

Tests validating command injection vulnerabilities.

**Test Coverage:**

- Command execution in transfer traces
- System command injection
- Path traversal via commands

**Example Tests:**

```python
def test_command_injection_in_traces(authenticated_client):
    """Test command injection vulnerability"""
    
def test_arbitrary_command_execution():
    """Test executing arbitrary system commands"""
```

### tests/security/test_deserialization.py

Tests validating insecure deserialization vulnerabilities.

**Test Coverage:**

- Pickle deserialization
- Malicious object unpickling
- Code execution via deserialization

**Example Tests:**

```python
def test_insecure_pickle_deserialization():
    """Test pickle deserialization vulnerability"""
    
def test_malicious_certificate_upload(authenticated_client):
    """Test malicious certificate processing"""
```

### tests/security/test_crypto_weaknesses.py

Tests validating weak cryptography implementations.

**Test Coverage:**

- DES encryption weakness
- Static key usage
- Weak checksum generation

**Example Tests:**

```python
def test_weak_des_encryption():
    """Test weak DES encryption"""
    
def test_static_encryption_key():
    """Test static key vulnerability"""
```

## Legacy Tests

### tests/test_integration.py

Legacy integration tests that may be superseded by tests in integration/.

### tests/test_setup.py

Tests validating test setup and configuration.

**Test Coverage:**

- pytest configuration
- Django settings
- Database connectivity
- Import validation

## Test File Naming Conventions

- Test files start with `test_`
- Test functions start with `test_`
- Test classes start with `Test`
- Descriptive names indicating what is tested

## Test Documentation

Each test should include:

```python
def test_user_login_success(client, test_user):
    """
    Test successful user login flow.
    
    Verifies that:
    - Valid credentials authenticate user
    - Session is created
    - User is redirected to dashboard
    """
    pass
```

## Fixture Scope

Fixtures can have different scopes:

- **function**: Default, new instance per test
- **class**: Shared within test class
- **module**: Shared within test module
- **session**: Shared across entire test session

```python
@pytest.fixture(scope="module")
def expensive_resource():
    """Shared across all tests in module"""
    pass
```

## Test Data Isolation

Tests use database transactions that are rolled back:

```python
@pytest.mark.django_db
def test_with_database(db):
    # Changes rolled back after test
    pass
```

## Parallel Test Execution

Tests are designed to run in parallel:

- No shared state between tests
- Database transaction isolation
- Independent fixtures
- No file system conflicts

## Related Documentation

- [Testing Overview](overview.md)
- [Unit Tests](unit-tests.md)
- [Integration Tests](integration-tests.md)
- [Security Tests](security-tests.md)
- [Test Configuration](configuration.md)
