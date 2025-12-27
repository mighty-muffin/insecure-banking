# Integration Tests

## Overview

Integration tests validate the interaction between multiple components, testing complete workflows and request/response cycles. These tests ensure that different parts of the application work together correctly.

## Test Categories

### Authentication Flow Tests

Located in `tests/integration/test_auth_flow.py`

#### Login Tests

```python
@pytest.mark.integration
def test_successful_login(client, db):
    """Test complete login workflow"""
    # Create test user
    Account(username="john", name="John", surname="Doe", password="test").save()
    
    # Attempt login
    response = client.post("/login", {
        "username": "john",
        "password": "test"
    })
    
    # Verify redirect to dashboard
    assert response.status_code == 302
    assert response.url == "/dashboard"
    
    # Verify session created
    assert "_auth_user_id" in client.session
```

#### Logout Tests

```python
@pytest.mark.integration
def test_logout_flow(authenticated_client):
    """Test logout workflow"""
    response = authenticated_client.get("/logout")
    
    assert response.status_code == 302
    assert response.url == "/login"
    assert "_auth_user_id" not in authenticated_client.session
```

#### Authentication Middleware Tests

Tests that verify unauthenticated users are redirected to login.

### Transfer Flow Tests

Located in `tests/integration/test_transfer_flow.py`

#### Transfer Creation Tests

```python
@pytest.mark.integration
def test_complete_transfer_flow(authenticated_client, db):
    """Test complete money transfer workflow"""
    # Setup accounts
    CashAccount(
        number="123456",
        username="john",
        description="Account 1",
        availableBalance=1000.0
    ).save()
    
    CashAccount(
        number="789012",
        username="jane",
        description="Account 2",
        availableBalance=500.0
    ).save()
    
    # Submit transfer
    response = authenticated_client.post("/transfer", {
        "fromAccount": "123456",
        "toAccount": "789012",
        "description": "Test transfer",
        "amount": 100.0,
        "fee": 5.0
    })
    
    # Verify transfer recorded
    transfers = Transfer.objects.filter(fromAccount="123456")
    assert len(transfers) == 1
    
    # Verify balances updated
    from_account = CashAccount.objects.get(number="123456")
    to_account = CashAccount.objects.get(number="789012")
    
    assert from_account.availableBalance == 895.0  # 1000 - 100 - 5
    assert to_account.availableBalance == 600.0     # 500 + 100
```

#### Transfer Confirmation Tests

Tests for two-step transfer process with confirmation page.

### Admin Flow Tests

Located in `tests/integration/test_admin_flow.py`

#### Admin Access Tests

```python
@pytest.mark.integration
def test_admin_view_access(authenticated_client):
    """Test accessing admin dashboard"""
    response = authenticated_client.get("/admin")
    
    assert response.status_code == 200
    assert b"Admin" in response.content
```

#### User Management Tests

Tests for viewing and managing users through admin interface.

### Database Integration Tests

Located in `tests/integration/test_database_integration.py`

#### Transaction Tests

```python
@pytest.mark.integration
def test_transfer_transaction_atomicity(db):
    """Test that transfer operations are atomic"""
    # Setup
    from_account = CashAccount(
        number="123456",
        username="john",
        description="Account 1",
        availableBalance=1000.0
    )
    from_account.save()
    
    # Simulate transfer error
    with pytest.raises(Exception):
        with transaction.atomic():
            transfer = Transfer(...)
            TransferService.insert_transfer(transfer)
            raise Exception("Simulated error")
    
    # Verify rollback
    from_account.refresh_from_db()
    assert from_account.availableBalance == 1000.0
```

## Test Characteristics

### Full Request/Response Cycle

Integration tests exercise complete workflows:

- HTTP request processing
- URL routing
- View execution
- Template rendering
- Response generation

### Database Operations

Tests interact with test database:

- Create test data
- Execute queries
- Verify data changes
- Test transaction behavior

### Component Interaction

Tests validate multiple components working together:

- Views calling services
- Services querying models
- Middleware processing requests
- Context processors adding data

## Test Client

Integration tests use Django's test client:

```python
# Anonymous client
response = client.get("/dashboard")

# Authenticated client
authenticated_client.get("/transfer")

# POST requests
client.post("/login", {"username": "john", "password": "test"})
```

## Fixtures

Common integration test fixtures:

```python
@pytest.fixture
def authenticated_client(client, test_user):
    """Provides authenticated test client"""
    client.force_login(test_user)
    return client

@pytest.fixture
def test_accounts(db):
    """Creates test account data"""
    # Create accounts, cash accounts, etc.
    pass
```

## Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/integration/test_auth_flow.py -v

# Run with database logging
pytest tests/integration/ -v --log-cli-level=DEBUG
```

## Test Data Management

### Setup

Each test sets up required data:

```python
def test_feature(db):
    # Create necessary test data
    account = Account(...).save()
    cash_account = CashAccount(...).save()
```

### Cleanup

Automatic cleanup through transaction rollback:

- No manual cleanup needed
- Test data isolated per test
- Database reset between tests

## Performance

Integration tests are slower than unit tests:

- Full application stack
- Database operations
- Template rendering

Run in parallel for faster execution:

```bash
pytest tests/integration/ -n auto
```

## Coverage

Integration tests verify:

- End-to-end workflows
- Component integration
- Request handling
- Error handling
- Security vulnerabilities

## Related Documentation

- [Testing Overview](overview.md)
- [Test Structure](structure.md)
- [Unit Tests](unit-tests.md)
- [Security Tests](security-tests.md)
