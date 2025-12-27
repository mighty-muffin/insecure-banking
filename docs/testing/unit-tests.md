# Unit Tests

## Overview

Unit tests validate individual components in isolation without external dependencies. They focus on testing specific functions, methods, and classes to ensure correct behavior.

## Test Files

### test_models.py

Tests for Django model definitions and behavior.

#### Model Creation Tests

```python
@pytest.mark.unit
def test_account_model_creation(db):
    """Test creating an Account model instance"""
    account = Account(
        username="testuser",
        name="Test",
        surname="User",
        password="testpass"
    )
    account.save()
    
    assert account.username == "testuser"
    assert account.name == "Test"
    assert account.surname == "User"
    assert account.password == "testpass"
```

#### Model Serialization Tests

```python
@pytest.mark.unit
def test_transfer_as_dict(db):
    """Test Transfer model serialization to dictionary"""
    transfer = Transfer(
        fromAccount="123456",
        toAccount="789012",
        description="Test transfer",
        amount=100.0,
        fee=5.0,
        username="testuser",
        date=datetime.now()
    )
    
    data = transfer.as_dict()
    
    assert data["fromAccount"] == "123456"
    assert data["toAccount"] == "789012"
    assert data["amount"] == 100.0
```

#### Model Validation Tests

Tests for field constraints and validation logic.

### test_services.py

Tests for service layer methods.

#### AccountService Tests

```python
@pytest.mark.unit
def test_find_users_by_username(db, test_user):
    """Test finding users by username"""
    accounts = AccountService.find_users_by_username("testuser")
    
    assert len(accounts) > 0
    assert accounts[0].username == "testuser"
```

#### CashAccountService Tests

```python
@pytest.mark.unit
def test_get_account_balance(db):
    """Test retrieving account balance"""
    cash_account = CashAccount(
        number="123456",
        username="testuser",
        description="Test Account",
        availableBalance=1000.0
    )
    cash_account.save()
    
    balance = CashAccountService.get_from_account_actual_amount("123456")
    
    assert balance == 1000.0
```

#### TransferService Tests

```python
@pytest.mark.unit
def test_insert_transfer(db):
    """Test inserting a transfer record"""
    transfer = Transfer(
        fromAccount="123456",
        toAccount="789012",
        description="Test",
        amount=100.0,
        fee=5.0,
        username="testuser",
        date=date.today()
    )
    
    TransferService.insert_transfer(transfer)
    
    transfers = Transfer.objects.filter(fromAccount="123456")
    assert len(transfers) == 1
```

### test_context_processors.py

Tests for Django context processors.

#### Version Info Tests

```python
@pytest.mark.unit
def test_version_info_context_processor():
    """Test version_info adds Git commit info to context"""
    from web.context_processors import version_info
    from django.http import HttpRequest
    
    request = HttpRequest()
    context = version_info(request)
    
    assert "git_commit" in context
    assert "repo_url" in context
```

## Test Characteristics

### Fast Execution

Unit tests run quickly:

- No network I/O
- Minimal database operations
- Isolated component testing

### Isolated Testing

Each test is independent:

- No shared state
- Database transactions rolled back
- Fixtures provide fresh data

### Single Responsibility

Each test validates one behavior:

- Clear test name
- Single assertion per test (ideally)
- Focused scope

## Running Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_models.py -v

# Run specific test
pytest tests/unit/test_models.py::test_account_model_creation -v

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=html
```

## Test Fixtures

Unit tests use fixtures from:

- `tests/conftest.py` (global fixtures)
- `tests/unit/conftest.py` (unit-specific fixtures)

Common fixtures:

- `db`: Database access
- `test_user`: Sample user account
- `mocker`: Mock object creation

## Mocking

Unit tests use pytest-mock for mocking dependencies:

```python
def test_with_mock(mocker):
    """Test using mocked dependency"""
    mock_service = mocker.patch('web.services.AccountService')
    mock_service.find_users_by_username.return_value = []
    
    # Test code using mocked service
```

## Test Coverage

Unit tests focus on:

- Model methods and properties
- Service layer business logic
- Utility functions
- Context processors
- Helper functions

Coverage target: Highest coverage for isolated components.

## Related Documentation

- [Testing Overview](overview.md)
- [Test Structure](structure.md)
- [Integration Tests](integration-tests.md)
- [Test Configuration](configuration.md)
