"""Integration test specific fixtures and utilities."""

import pytest
from django.test import TransactionTestCase


@pytest.fixture
def live_server_url():
    """URL for live server testing."""
    return "http://testserver"


@pytest.fixture
def api_client():
    """API client for integration testing."""
    from django.test import Client
    return Client()


@pytest.fixture
def authenticated_client(client, user_data):
    """Client with authenticated user."""
    from django.contrib.auth.models import User

    user = User.objects.create_user(**user_data)
    client.force_login(user)
    return client


@pytest.fixture
def full_database_setup(db):
    """Complete database setup with all models."""
    from django.contrib.auth.models import User
    from web.models import Account, Transaction

    # Create multiple users
    users = []
    for i in range(3):
        user = User.objects.create_user(
            username=f"user{i}",
            email=f"user{i}@example.com",
            password="testpass123",
            first_name=f"User{i}",
            last_name="Test"
        )
        users.append(user)

    # Create accounts for each user
    accounts = []
    for i, user in enumerate(users):
        account = Account.objects.create(
            user=user,
            account_number=f"12345678{i:02d}",
            balance=1000.00 * (i + 1),
            account_type="checking" if i % 2 == 0 else "savings"
        )
        accounts.append(account)

    # Create some transactions
    transactions = []
    for i, account in enumerate(accounts):
        transaction = Transaction.objects.create(
            account=account,
            amount=100.00 * (i + 1),
            description=f"Test transaction {i}",
            transaction_type="deposit" if i % 2 == 0 else "withdrawal"
        )
        transactions.append(transaction)

    return {
        "users": users,
        "accounts": accounts,
        "transactions": transactions
    }
