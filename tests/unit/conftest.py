"""Unit test specific fixtures and utilities."""

import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_user():
    """Mock Django User object."""
    user = Mock()
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.first_name = "Test"
    user.last_name = "User"
    user.is_authenticated = True
    user.is_active = True
    user.is_staff = False
    user.is_superuser = False
    return user


@pytest.fixture
def mock_account():
    """Mock Account model object."""
    account = Mock()
    account.id = 1
    account.account_number = "1234567890"
    account.balance = 1000.00
    account.account_type = "checking"
    account.is_active = True
    return account


@pytest.fixture
def mock_transaction():
    """Mock Transaction model object."""
    transaction = Mock()
    transaction.id = 1
    transaction.amount = 100.00
    transaction.description = "Test transaction"
    transaction.transaction_type = "transfer"
    transaction.status = "completed"
    return transaction


@pytest.fixture
def mock_request():
    """Mock Django request object."""
    request = Mock()
    request.method = "GET"
    request.path = "/test/"
    request.user = Mock()
    request.user.is_authenticated = True
    request.GET = {}
    request.POST = {}
    request.session = {}
    request.META = {}
    return request


@pytest.fixture
def mock_response():
    """Mock Django response object."""
    response = Mock()
    response.status_code = 200
    response.content = b"Test content"
    response.context = {}
    return response
