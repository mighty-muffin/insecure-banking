"""Test to verify basic test setup is working."""

import pytest
from tests.utils import generate_random_string, TestDataFactory


def test_basic_setup():
    """Test that basic test infrastructure is working."""
    # Test utility functions
    random_str = generate_random_string(10)
    assert len(random_str) == 10
    assert random_str.isalnum()


def test_test_data_factory():
    """Test that TestDataFactory is working."""
    factory = TestDataFactory()

    # Test user data generation
    user_data = factory.create_user()
    assert "username" in user_data
    assert "email" in user_data
    assert "password" in user_data

    # Test account data generation
    account_data = factory.create_account()
    assert "account_number" in account_data
    assert "balance" in account_data
    assert "account_type" in account_data

    # Test transaction data generation
    transaction_data = factory.create_transaction()
    assert "amount" in transaction_data
    assert "description" in transaction_data
    assert "transaction_type" in transaction_data


@pytest.mark.unit
def test_marker_functionality():
    """Test that pytest markers are working."""
    assert True


class TestBasicPytestFeatures:
    """Test class to verify pytest class-based testing."""

    def test_class_based_test(self):
        """Test that class-based tests work."""
        assert True

    def test_with_fixture(self, user_data):
        """Test that fixtures from conftest.py work."""
        assert "username" in user_data
        assert "email" in user_data
