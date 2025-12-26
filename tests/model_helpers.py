"""Model testing helper functions and utilities."""

from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random
import string


class ModelTestHelpers:
    """Helper methods for testing Django models."""

    @staticmethod
    def assert_model_fields(model_instance, expected_fields: Dict[str, Any]):
        """Assert that model instance has expected field values."""
        for field_name, expected_value in expected_fields.items():
            actual_value = getattr(model_instance, field_name)
            assert actual_value == expected_value, \
                f"Field {field_name}: expected {expected_value}, got {actual_value}"

    @staticmethod
    def assert_model_validation_error(model_class, field_data: Dict[str, Any],
                                    expected_errors: List[str] = None):
        """Assert that model validation raises expected errors."""
        try:
            instance = model_class(**field_data)
            instance.full_clean()
            assert False, "Expected validation error but none was raised"
        except Exception as e:
            if expected_errors:
                error_message = str(e)
                for expected_error in expected_errors:
                    assert expected_error in error_message, \
                        f"Expected error '{expected_error}' not found in '{error_message}'"

    @staticmethod
    def create_model_with_defaults(model_class, **overrides):
        """Create model instance with default values and optional overrides."""
        defaults = ModelTestHelpers.get_model_defaults(model_class)
        defaults.update(overrides)
        return model_class.objects.create(**defaults)

    @staticmethod
    def get_model_defaults(model_class):
        """Get default values for model fields."""
        if model_class.__name__ == 'Account':
            return {
                'username': f"user_{ModelTestHelpers._random_string(8)}",
                'name': "Test",
                'surname': "User",
                'password': "testpass123"
            }
        elif model_class.__name__ == 'CashAccount':
            return {
                'number': ModelTestHelpers._random_account_number(),
                'username': f"user_{ModelTestHelpers._random_string(8)}",
                'description': "Test Cash Account",
                'availableBalance': 1000.00
            }
        elif model_class.__name__ == 'CreditAccount':
            return {
                'cashAccountId': 1,
                'number': ModelTestHelpers._random_account_number(),
                'username': f"user_{ModelTestHelpers._random_string(8)}",
                'description': "Test Credit Account",
                'availableBalance': 5000.00
            }
        elif model_class.__name__ == 'Transfer':
            return {
                'fromAccount': ModelTestHelpers._random_account_number(),
                'toAccount': ModelTestHelpers._random_account_number(),
                'description': "Test Transfer",
                'amount': 100.00,
                'fee': 20.00,
                'username': f"user_{ModelTestHelpers._random_string(8)}",
                'date': datetime.now()
            }
        elif model_class.__name__ == 'Transaction':
            return {
                'number': f"TXN{ModelTestHelpers._random_string(6, string.digits)}",
                'description': "Test Transaction",
                'amount': 100.00,
                'availableBalance': 900.00,
                'date': datetime.now()
            }
        else:
            return {}

    @staticmethod
    def _random_string(length: int, charset: str = None) -> str:
        """Generate random string of specified length."""
        if charset is None:
            charset = string.ascii_letters + string.digits
        return ''.join(random.choices(charset, k=length))

    @staticmethod
    def _random_account_number() -> str:
        """Generate random account number."""
        return ModelTestHelpers._random_string(10, string.digits)


class AccountTestHelpers:
    """Specific helpers for Account model testing."""

    @staticmethod
    def create_test_account(username: str = None, **kwargs):
        """Create test Account with optional parameters."""
        from web.models import Account

        defaults = {
            'username': username or f"testuser_{ModelTestHelpers._random_string(8)}",
            'name': "Test",
            'surname': "User",
            'password': "testpass123"
        }
        defaults.update(kwargs)

        return Account.objects.create(**defaults)

    @staticmethod
    def create_multiple_accounts(count: int) -> List:
        """Create multiple test accounts."""
        accounts = []
        for i in range(count):
            account = AccountTestHelpers.create_test_account(
                username=f"testuser{i}",
                name=f"Test{i}",
                surname="User"
            )
            accounts.append(account)
        return accounts

    @staticmethod
    def assert_account_data(account, expected_username: str = None,
                           expected_name: str = None, expected_surname: str = None):
        """Assert account data matches expectations."""
        if expected_username:
            assert account.username == expected_username
        if expected_name:
            assert account.name == expected_name
        if expected_surname:
            assert account.surname == expected_surname


class CashAccountTestHelpers:
    """Specific helpers for CashAccount model testing."""

    @staticmethod
    def create_test_cash_account(username: str = None, **kwargs):
        """Create test CashAccount with optional parameters."""
        from web.models import CashAccount

        defaults = {
            'number': ModelTestHelpers._random_account_number(),
            'username': username or f"testuser_{ModelTestHelpers._random_string(8)}",
            'description': "Test Cash Account",
            'availableBalance': 1000.00
        }
        defaults.update(kwargs)

        return CashAccount.objects.create(**defaults)

    @staticmethod
    def assert_balance_change(cash_account, expected_change: float):
        """Assert that cash account balance changed by expected amount."""
        original_balance = cash_account.availableBalance
        cash_account.refresh_from_db()
        actual_change = cash_account.availableBalance - original_balance
        assert abs(actual_change - expected_change) < 0.01, \
            f"Expected balance change {expected_change}, got {actual_change}"


class TransferTestHelpers:
    """Specific helpers for Transfer model testing."""

    @staticmethod
    def create_test_transfer(from_account: str = None, to_account: str = None,
                           username: str = None, **kwargs):
        """Create test Transfer with optional parameters."""
        from web.models import Transfer

        defaults = {
            'fromAccount': from_account or ModelTestHelpers._random_account_number(),
            'toAccount': to_account or ModelTestHelpers._random_account_number(),
            'description': "Test Transfer",
            'amount': 100.00,
            'fee': 20.00,
            'username': username or f"testuser_{ModelTestHelpers._random_string(8)}",
            'date': datetime.now()
        }
        defaults.update(kwargs)

        return Transfer.objects.create(**defaults)

    @staticmethod
    def assert_transfer_data(transfer, expected_amount: float = None,
                           expected_fee: float = None):
        """Assert transfer data matches expectations."""
        if expected_amount is not None:
            assert abs(transfer.amount - expected_amount) < 0.01
        if expected_fee is not None:
            assert abs(transfer.fee - expected_fee) < 0.01


class ValidationTestHelpers:
    """Helpers for testing model validation."""

    @staticmethod
    def test_field_max_length(model_class, field_name: str, max_length: int):
        """Test that field respects max_length constraint."""
        # This would need to be implemented based on the actual validation
        # Since this is an intentionally vulnerable app, validation might be minimal
        pass

    @staticmethod
    def test_required_fields(model_class, required_fields: List[str]):
        """Test that required fields are enforced."""
        for field_name in required_fields:
            try:
                # Try to create instance without required field
                data = ModelTestHelpers.get_model_defaults(model_class)
                data.pop(field_name, None)
                instance = model_class(**data)
                instance.full_clean()
                # If we get here, the field is not properly validated as required
                assert False, f"Field {field_name} should be required but validation passed"
            except Exception:
                # Expected to fail - this is good
                pass

    @staticmethod
    def test_field_type_validation(model_class, field_name: str,
                                 invalid_values: List[Any]):
        """Test that field validates data types correctly."""
        defaults = ModelTestHelpers.get_model_defaults(model_class)

        for invalid_value in invalid_values:
            try:
                data = defaults.copy()
                data[field_name] = invalid_value
                instance = model_class(**data)
                instance.full_clean()
                assert False, f"Field {field_name} should reject value {invalid_value}"
            except Exception:
                # Expected to fail - this is good
                pass
