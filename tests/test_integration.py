"""Integration test to verify pytest-django setup."""

import pytest
from django.test import TestCase


@pytest.mark.django_db
def test_django_db_access(sample_account):
    """Test that Django database access works with pytest."""
    assert sample_account.username == "testuser"
    assert sample_account.name == "Test"
    assert sample_account.surname == "User"


@pytest.mark.django_db
def test_factory_fixtures(account_factory, cash_account_factory):
    """Test that factory fixtures work correctly."""
    # Create account using factory
    account = account_factory(username="factoryuser")
    assert account.username == "factoryuser"

    # Create cash account using factory
    cash_account = cash_account_factory(username=account.username, availableBalance=2000.00)
    assert cash_account.username == account.username
    assert cash_account.availableBalance == 2000.00


def test_mock_services(mock_transfer_service, mock_account_service):
    """Test that mock service fixtures work correctly."""
    # Test mock transfer service
    result = mock_transfer_service.process_transfer()
    assert result["success"] is True
    assert "transaction_id" in result

    # Test mock account service
    assert mock_account_service.authenticate_user() is True
    assert mock_account_service.get_account_balance() == 1000.00


@pytest.mark.unit
def test_unit_marker():
    """Test that unit marker works."""
    assert True


@pytest.mark.integration
def test_integration_marker():
    """Test that integration marker works."""
    assert True


@pytest.mark.security
def test_security_marker():
    """Test that security marker works."""
    assert True


class TestDjangoTestCase(TestCase):
    """Test that Django TestCase still works alongside pytest."""

    def test_django_testcase_functionality(self):
        """Test Django TestCase functionality."""
        from web.models import Account

        account = Account.objects.create(
            username="djangotest",
            name="Django",
            surname="Test",
            password="testpass"
        )

        self.assertEqual(account.username, "djangotest")
        self.assertEqual(account.name, "Django")


@pytest.mark.django_db
def test_model_creation_and_queries():
    """Test basic model operations work correctly."""
    from web.models import Account, CashAccount

    # Create account
    account = Account.objects.create(
        username="querytest",
        name="Query",
        surname="Test",
        password="testpass"
    )

    # Verify it was created
    retrieved_account = Account.objects.get(username="querytest")
    assert retrieved_account.name == "Query"

    # Create related cash account
    cash_account = CashAccount.objects.create(
        number="9876543210",
        username=account.username,
        description="Test Query Account",
        availableBalance=1500.00
    )

    # Verify cash account
    assert cash_account.username == account.username
    assert cash_account.availableBalance == 1500.00


@pytest.mark.django_db
def test_database_transactions():
    """Test database transaction handling."""
    from web.models import Account
    from django.db import transaction

    initial_count = Account.objects.count()

    try:
        with transaction.atomic():
            Account.objects.create(
                username="transtest1",
                name="Trans",
                surname="Test1",
                password="test"
            )
            Account.objects.create(
                username="transtest2",
                name="Trans",
                surname="Test2",
                password="test"
            )
            # This should work fine

        # Verify both accounts were created
        assert Account.objects.count() == initial_count + 2

    except Exception as e:
        pytest.fail(f"Transaction test failed: {e}")


def test_pytest_configuration():
    """Test that pytest is configured correctly."""
    import pytest
    import django
    from django.conf import settings

    # Verify Django is set up
    assert hasattr(django, 'VERSION')
    assert settings.configured

    # Verify test settings
    db_name = str(settings.DATABASES['default']['NAME'])
    assert ':memory:' in db_name or 'mode=memory' in db_name

    # Verify pytest markers are available
    assert hasattr(pytest, 'mark')
    assert hasattr(pytest.mark, 'django_db')


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v"])
