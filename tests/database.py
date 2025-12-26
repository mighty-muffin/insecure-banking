"""Database management utilities for testing."""

import os
from django.core.management import call_command
from django.db import connection
from django.test.utils import setup_test_environment, teardown_test_environment


class TestDatabaseManager:
    """Manages test database setup and teardown."""

    @staticmethod
    def setup_test_database():
        """Set up test database with proper configuration."""
        setup_test_environment()

        # Create tables (since we disable migrations)
        call_command('migrate', verbosity=0, interactive=False, run_syncdb=True)

    @staticmethod
    def teardown_test_database():
        """Clean up test database."""
        teardown_test_environment()

    @staticmethod
    def reset_database():
        """Reset database to clean state."""
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF;")

        # Get all tables
        tables = connection.introspection.table_names()

        # Delete all data from tables
        for table in tables:
            cursor.execute(f'DELETE FROM "{table}";')

        cursor.execute("PRAGMA foreign_keys = ON;")
        connection.commit()

    @staticmethod
    def populate_test_data():
        """Populate database with standard test data."""
        from web.models import Account, CashAccount, CreditAccount, Transfer, Transaction
        from datetime import datetime

        # Create test accounts
        accounts = []
        for i in range(3):
            account = Account.objects.create(
                username=f"testuser{i}",
                name=f"Test{i}",
                surname="User",
                password="testpass123"
            )
            accounts.append(account)

        # Create cash accounts
        cash_accounts = []
        for i, account in enumerate(accounts):
            cash_account = CashAccount.objects.create(
                number=f"12345678{i:02d}",
                username=account.username,
                description=f"Cash Account {i}",
                availableBalance=1000.00 * (i + 1)
            )
            cash_accounts.append(cash_account)

        # Create credit accounts
        credit_accounts = []
        for i, account in enumerate(accounts):
            credit_account = CreditAccount.objects.create(
                cashAccountId=i + 1,
                number=f"98765432{i:02d}",
                username=account.username,
                description=f"Credit Account {i}",
                availableBalance=5000.00 * (i + 1)
            )
            credit_accounts.append(credit_account)

        # Create transfers
        transfers = []
        for i in range(len(accounts) - 1):
            transfer = Transfer.objects.create(
                fromAccount=cash_accounts[i].number,
                toAccount=cash_accounts[i + 1].number,
                description=f"Test Transfer {i}",
                amount=100.00 * (i + 1),
                fee=20.00,
                username=accounts[i].username,
                date=datetime.now()
            )
            transfers.append(transfer)

        # Create transactions
        transactions = []
        for i in range(5):
            transaction = Transaction.objects.create(
                number=f"TXN{i:06d}",
                description=f"Test Transaction {i}",
                amount=50.00 * (i + 1),
                availableBalance=1000.00 - (50.00 * (i + 1)),
                date=datetime.now()
            )
            transactions.append(transaction)

        return {
            'accounts': accounts,
            'cash_accounts': cash_accounts,
            'credit_accounts': credit_accounts,
            'transfers': transfers,
            'transactions': transactions
        }


def setup_module_database():
    """Set up database for module-level testing."""
    TestDatabaseManager.setup_test_database()


def teardown_module_database():
    """Tear down database after module testing."""
    TestDatabaseManager.teardown_test_database()


def reset_database_between_tests():
    """Reset database between individual tests."""
    TestDatabaseManager.reset_database()


def create_test_data_set(data_type="minimal"):
    """Create different sets of test data."""
    if data_type == "minimal":
        return _create_minimal_test_data()
    elif data_type == "full":
        return TestDatabaseManager.populate_test_data()
    elif data_type == "security":
        return _create_security_test_data()
    else:
        raise ValueError(f"Unknown data type: {data_type}")


def _create_minimal_test_data():
    """Create minimal test data set."""
    from web.models import Account, CashAccount

    account = Account.objects.create(
        username="testuser",
        name="Test",
        surname="User",
        password="testpass123"
    )

    cash_account = CashAccount.objects.create(
        number="1234567890",
        username=account.username,
        description="Test Cash Account",
        availableBalance=1000.00
    )

    return {
        'account': account,
        'cash_account': cash_account
    }


def _create_security_test_data():
    """Create test data specifically for security testing."""
    from web.models import Account, CashAccount, Transfer
    from datetime import datetime

    # Create accounts with various security test scenarios
    accounts = []

    # Normal account
    normal_account = Account.objects.create(
        username="normal_user",
        name="Normal",
        surname="User",
        password="securepass123"
    )
    accounts.append(normal_account)

    # Account with weak password
    weak_account = Account.objects.create(
        username="weak_user",
        name="Weak",
        surname="User",
        password="123456"
    )
    accounts.append(weak_account)

    # Account with SQL injection attempt in name
    sqli_account = Account.objects.create(
        username="sqli_user",
        name="'; DROP TABLE accounts; --",
        surname="Hacker",
        password="hackerpass"
    )
    accounts.append(sqli_account)

    # Create corresponding cash accounts
    cash_accounts = []
    for i, account in enumerate(accounts):
        cash_account = CashAccount.objects.create(
            number=f"SEC{i:07d}",
            username=account.username,
            description=f"Security Test Account {i}",
            availableBalance=1000.00
        )
        cash_accounts.append(cash_account)

    # Create suspicious transfers
    suspicious_transfer = Transfer.objects.create(
        fromAccount=cash_accounts[0].number,
        toAccount=cash_accounts[1].number,
        description="<script>alert('XSS')</script>",
        amount=999999.00,  # Suspiciously large amount
        fee=0.00,  # No fee (suspicious)
        username=accounts[0].username,
        date=datetime.now()
    )

    return {
        'accounts': accounts,
        'cash_accounts': cash_accounts,
        'suspicious_transfer': suspicious_transfer
    }
