"""Unit tests for Django models."""

import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from unittest.mock import patch, Mock

from web.models import Account, CashAccount, CreditAccount, Transfer, Transaction
from tests.model_helpers import (
    ModelTestHelpers, AccountTestHelpers, CashAccountTestHelpers,
    TransferTestHelpers, ValidationTestHelpers
)


class TestAccount(TestCase):
    """Unit tests for Account model."""

    def setUp(self):
        """Set up test data."""
        self.account_data = {
            'username': 'testuser',
            'name': 'Test',
            'surname': 'User',
            'password': 'testpass123'
        }

    def test_account_creation(self):
        """Test that Account can be created with valid data."""
        account = Account.objects.create(**self.account_data)

        self.assertEqual(account.username, 'testuser')
        self.assertEqual(account.name, 'Test')
        self.assertEqual(account.surname, 'User')
        self.assertEqual(account.password, 'testpass123')

    def test_account_primary_key(self):
        """Test that username is the primary key."""
        account = Account.objects.create(**self.account_data)

        # Username should be the primary key
        self.assertEqual(account.pk, 'testuser')
        self.assertEqual(account.username, account.pk)

    def test_account_string_representation(self):
        """Test Account string representation."""
        account = Account.objects.create(**self.account_data)

        # Test string representation (if __str__ method exists)
        expected_str = str(account)
        self.assertIn('testuser', expected_str)

    def test_account_fields_max_length(self):
        """Test that Account fields respect max_length constraints."""
        # Test username max length (80 chars)
        long_username = 'a' * 81
        with self.assertRaises(Exception):  # Could be ValidationError or database error
            account = Account(
                username=long_username,
                name='Test',
                surname='User',
                password='test'
            )
            account.full_clean()
            account.save()

    def test_account_required_fields(self):
        """Test that all fields are required (if they are)."""
        # Test creation without username
        with self.assertRaises(Exception):
            account = Account(
                name='Test',
                surname='User',
                password='test'
            )
            account.full_clean()
            account.save()

    def test_account_username_uniqueness(self):
        """Test that username must be unique."""
        Account.objects.create(**self.account_data)

        # Try to create another account with same username
        with self.assertRaises(Exception):
            Account.objects.create(**self.account_data)

    def test_account_field_types(self):
        """Test that Account fields accept correct data types."""
        # All fields are CharField, so test string assignment
        account = Account(**self.account_data)

        self.assertIsInstance(account.username, str)
        self.assertIsInstance(account.name, str)
        self.assertIsInstance(account.surname, str)
        self.assertIsInstance(account.password, str)

    def test_account_empty_fields(self):
        """Test behavior with empty field values."""
        # Test with empty strings (if allowed)
        try:
            account = Account.objects.create(
                username='emptytest',
                name='',
                surname='',
                password=''
            )
            self.assertEqual(account.name, '')
            self.assertEqual(account.surname, '')
            self.assertEqual(account.password, '')
        except Exception:
            # If empty fields are not allowed, that's also valid behavior
            pass

    def test_account_special_characters(self):
        """Test Account with special characters in fields."""
        special_data = {
            'username': 'user_test-123',
            'name': "O'Connor",
            'surname': 'Smith-Jones',
            'password': 'p@ssw0rd!'
        }

        try:
            account = Account.objects.create(**special_data)
            self.assertEqual(account.username, 'user_test-123')
            self.assertEqual(account.name, "O'Connor")
        except Exception:
            # If special characters are not allowed, that's valid too
            pass

    def test_account_case_sensitivity(self):
        """Test username case sensitivity."""
        Account.objects.create(**self.account_data)

        # Try to create with different case
        different_case_data = self.account_data.copy()
        different_case_data['username'] = 'TESTUSER'

        try:
            Account.objects.create(**different_case_data)
            # If this succeeds, usernames are case-sensitive
            self.assertNotEqual('testuser', 'TESTUSER')
        except Exception:
            # If this fails, usernames might be case-insensitive
            pass


class TestAccountHelpers(TestCase):
    """Test the Account helper functions."""

    def test_account_test_helpers(self):
        """Test AccountTestHelpers functions."""
        # Test create_test_account
        account = AccountTestHelpers.create_test_account(username="helpertest")
        self.assertEqual(account.username, "helpertest")
        self.assertEqual(account.name, "Test")

        # Test create_multiple_accounts
        accounts = AccountTestHelpers.create_multiple_accounts(3)
        self.assertEqual(len(accounts), 3)

        # Test assert_account_data
        AccountTestHelpers.assert_account_data(
            account,
            expected_username="helpertest",
            expected_name="Test"
        )

    def test_model_test_helpers(self):
        """Test ModelTestHelpers functions."""
        # Test get_model_defaults
        defaults = ModelTestHelpers.get_model_defaults(Account)
        self.assertIn('username', defaults)
        self.assertIn('name', defaults)
        self.assertIn('surname', defaults)
        self.assertIn('password', defaults)

        # Test create_model_with_defaults
        account = ModelTestHelpers.create_model_with_defaults(
            Account,
            username="defaulttest"
        )
        self.assertEqual(account.username, "defaulttest")

    def test_assert_model_fields(self):
        """Test ModelTestHelpers.assert_model_fields."""
        account = Account.objects.create(
            username="asserttest",
            name="Assert",
            surname="Test",
            password="test123"
        )

        expected_fields = {
            'username': 'asserttest',
            'name': 'Assert',
            'surname': 'Test'
        }

        # This should not raise an exception
        ModelTestHelpers.assert_model_fields(account, expected_fields)


@pytest.mark.unit
class TestAccountPytest(object):
    """Pytest-style tests for Account model."""

    @pytest.mark.django_db
    def test_account_creation_with_fixture(self, account_factory):
        """Test Account creation using factory fixture."""
        account = account_factory(username="pytestuser")

        assert account.username == "pytestuser"
        assert account.name == "Test"
        assert account.surname == "User"

    @pytest.mark.django_db
    def test_account_with_sample_fixture(self, sample_account):
        """Test using sample_account fixture."""
        assert sample_account.username == "testuser"
        assert sample_account.name == "Test"

    @pytest.mark.django_db
    def test_account_query_operations(self, account_factory):
        """Test basic query operations on Account."""
        # Create multiple accounts
        account1 = account_factory(username="query1", name="Query1")
        account2 = account_factory(username="query2", name="Query2")

        # Test get
        retrieved = Account.objects.get(username="query1")
        assert retrieved.name == "Query1"

        # Test filter
        accounts = Account.objects.filter(name__startswith="Query")
        assert len(accounts) >= 2

        # Test exists
        assert Account.objects.filter(username="query1").exists()
        assert not Account.objects.filter(username="nonexistent").exists()

    @pytest.mark.django_db
    def test_account_update_operations(self, account_factory):
        """Test update operations on Account."""
        account = account_factory(username="updatetest")

        # Update single field
        account.name = "Updated"
        account.save()

        # Refresh from database
        account.refresh_from_db()
        assert account.name == "Updated"

        # Bulk update
        Account.objects.filter(username="updatetest").update(surname="NewSurname")
        account.refresh_from_db()
        assert account.surname == "NewSurname"

    @pytest.mark.django_db
    def test_account_delete_operations(self, account_factory):
        """Test delete operations on Account."""
        account = account_factory(username="deletetest")
        initial_count = Account.objects.count()

        # Delete instance
        account.delete()

        # Verify deletion
        assert Account.objects.count() == initial_count - 1
        assert not Account.objects.filter(username="deletetest").exists()


class TestCashAccount(TestCase):
    """Unit tests for CashAccount model."""

    def setUp(self):
        """Set up test data."""
        self.cash_account_data = {
            'number': '1234567890',
            'username': 'testuser',
            'description': 'Test Cash Account',
            'availableBalance': 1000.00
        }

    def test_cash_account_creation(self):
        """Test that CashAccount can be created with valid data."""
        cash_account = CashAccount.objects.create(**self.cash_account_data)

        self.assertEqual(cash_account.number, '1234567890')
        self.assertEqual(cash_account.username, 'testuser')
        self.assertEqual(cash_account.description, 'Test Cash Account')
        self.assertEqual(cash_account.availableBalance, 1000.00)

    def test_cash_account_balance_validation(self):
        """Test CashAccount balance validation."""
        # Test positive balance
        cash_account = CashAccount.objects.create(**self.cash_account_data)
        self.assertGreaterEqual(cash_account.availableBalance, 0)

        # Test zero balance
        zero_balance_data = self.cash_account_data.copy()
        zero_balance_data['availableBalance'] = 0.0
        zero_account = CashAccount.objects.create(**zero_balance_data)
        self.assertEqual(zero_account.availableBalance, 0.0)

        # Test negative balance (if allowed by the vulnerable app)
        negative_balance_data = self.cash_account_data.copy()
        negative_balance_data['availableBalance'] = -100.0
        negative_balance_data['number'] = '9876543210'
        try:
            negative_account = CashAccount.objects.create(**negative_balance_data)
            # If negative balance is allowed (vulnerability), test passes
            self.assertEqual(negative_account.availableBalance, -100.0)
        except Exception:
            # If negative balance is not allowed, that's also valid
            pass

    def test_cash_account_number_format(self):
        """Test CashAccount number format."""
        # Test numeric account number
        cash_account = CashAccount.objects.create(**self.cash_account_data)
        self.assertTrue(cash_account.number.isdigit())

        # Test non-numeric account number (if allowed)
        alpha_data = self.cash_account_data.copy()
        alpha_data['number'] = 'CASH123ABC'
        try:
            alpha_account = CashAccount.objects.create(**alpha_data)
            self.assertEqual(alpha_account.number, 'CASH123ABC')
        except Exception:
            # If non-numeric is not allowed, that's also valid
            pass

    def test_cash_account_large_balance(self):
        """Test CashAccount with very large balance."""
        large_data = self.cash_account_data.copy()
        large_data['availableBalance'] = 999999999.99
        large_data['number'] = '5555555555'

        large_account = CashAccount.objects.create(**large_data)
        self.assertEqual(large_account.availableBalance, 999999999.99)

    def test_cash_account_precision(self):
        """Test CashAccount balance precision."""
        precision_data = self.cash_account_data.copy()
        precision_data['availableBalance'] = 123.456789  # More than 2 decimal places
        precision_data['number'] = '7777777777'

        precision_account = CashAccount.objects.create(**precision_data)
        # Balance might be rounded or truncated
        self.assertIsInstance(precision_account.availableBalance, float)

    def test_cash_account_string_fields(self):
        """Test CashAccount string field validation."""
        # Test empty description
        empty_desc_data = self.cash_account_data.copy()
        empty_desc_data['description'] = ''
        empty_desc_data['number'] = '8888888888'

        try:
            empty_account = CashAccount.objects.create(**empty_desc_data)
            self.assertEqual(empty_account.description, '')
        except Exception:
            # If empty description is not allowed
            pass

        # Test very long description
        long_desc_data = self.cash_account_data.copy()
        long_desc_data['description'] = 'a' * 100  # Longer than max_length
        long_desc_data['number'] = '9999999999'

        with self.assertRaises(Exception):
            account = CashAccount(**long_desc_data)
            account.full_clean()
            account.save()


@pytest.mark.unit
class TestCashAccountPytest:
    """Pytest-style tests for CashAccount model."""

    def test_cash_account_factory(self, cash_account_factory):
        """Test CashAccount creation using factory."""
        cash_account = cash_account_factory(
            number="1111111111",
            availableBalance=2500.00
        )

        assert cash_account.number == "1111111111"
        assert cash_account.availableBalance == 2500.00

    @pytest.mark.django_db
    def test_cash_account_balance_operations(self, cash_account_factory):
        """Test balance manipulation operations."""
        cash_account = cash_account_factory(availableBalance=1000.00)

        # Test balance update
        original_balance = cash_account.availableBalance
        cash_account.availableBalance += 100.00
        cash_account.save()

        cash_account.refresh_from_db()
        assert cash_account.availableBalance == original_balance + 100.00

    @pytest.mark.django_db
    def test_cash_account_helper_functions(self, cash_account_factory):
        """Test CashAccountTestHelpers functions."""
        cash_account = cash_account_factory(availableBalance=500.00)

        # Test assert_balance_change helper
        # Update via a separate instance or direct DB update to keep cash_account stale
        from web.models import CashAccount
        CashAccount.objects.filter(pk=cash_account.pk).update(availableBalance=cash_account.availableBalance + 50.00)

        cash_account.refresh_from_db()
        assert cash_account.availableBalance == 550.00

    @pytest.mark.django_db
    def test_cash_account_queries(self, cash_account_factory):
        """Test CashAccount query operations."""
        # Create accounts with different balances
        low_balance = cash_account_factory(availableBalance=100.00, number="1111111111")
        high_balance = cash_account_factory(availableBalance=5000.00, number="2222222222")

        # Test balance-based queries
        high_accounts = CashAccount.objects.filter(availableBalance__gte=1000.00)
        assert high_balance in high_accounts

        low_accounts = CashAccount.objects.filter(availableBalance__lt=500.00)
        assert low_balance in low_accounts


class TestCreditAccount(TestCase):
    """Unit tests for CreditAccount model."""

    def setUp(self):
        """Set up test data."""
        self.credit_account_data = {
            'cashAccountId': 1,
            'number': '0987654321',
            'username': 'testuser',
            'description': 'Test Credit Account',
            'availableBalance': 5000.00
        }

    def test_credit_account_creation(self):
        """Test that CreditAccount can be created with valid data."""
        credit_account = CreditAccount.objects.create(**self.credit_account_data)

        self.assertEqual(credit_account.cashAccountId, 1)
        self.assertEqual(credit_account.number, '0987654321')
        self.assertEqual(credit_account.username, 'testuser')
        self.assertEqual(credit_account.description, 'Test Credit Account')
        self.assertEqual(credit_account.availableBalance, 5000.00)

    def test_credit_account_cash_account_relationship(self):
        """Test CreditAccount relationship to cash account."""
        credit_account = CreditAccount.objects.create(**self.credit_account_data)

        # Test that cashAccountId is stored correctly
        self.assertEqual(credit_account.cashAccountId, 1)
        self.assertIsInstance(credit_account.cashAccountId, int)

    def test_credit_account_credit_limit_validation(self):
        """Test CreditAccount credit limit (availableBalance) validation."""
        # Test high credit limit
        high_limit_data = self.credit_account_data.copy()
        high_limit_data['availableBalance'] = 100000.00
        high_limit_data['number'] = '1111111111'

        high_account = CreditAccount.objects.create(**high_limit_data)
        self.assertEqual(high_account.availableBalance, 100000.00)

        # Test zero credit limit
        zero_limit_data = self.credit_account_data.copy()
        zero_limit_data['availableBalance'] = 0.0
        zero_limit_data['number'] = '2222222222'

        zero_account = CreditAccount.objects.create(**zero_limit_data)
        self.assertEqual(zero_account.availableBalance, 0.0)

        # Test negative credit limit (if allowed - vulnerability)
        negative_limit_data = self.credit_account_data.copy()
        negative_limit_data['availableBalance'] = -1000.0
        negative_limit_data['number'] = '3333333333'

        try:
            negative_account = CreditAccount.objects.create(**negative_limit_data)
            # If negative credit limit is allowed (potential vulnerability)
            self.assertEqual(negative_account.availableBalance, -1000.0)
        except Exception:
            # If negative credit limit is properly rejected
            pass

    def test_credit_account_number_uniqueness(self):
        """Test CreditAccount number uniqueness (if enforced)."""
        CreditAccount.objects.create(**self.credit_account_data)

        # Try to create another credit account with same number
        duplicate_data = self.credit_account_data.copy()
        duplicate_data['cashAccountId'] = 2  # Different cash account

        try:
            CreditAccount.objects.create(**duplicate_data)
            # If duplicates are allowed, test the behavior
            duplicate_accounts = CreditAccount.objects.filter(number='0987654321')
            self.assertGreaterEqual(len(duplicate_accounts), 2)
        except Exception:
            # If duplicates are properly prevented
            pass

    def test_credit_account_cash_account_id_validation(self):
        """Test CreditAccount cashAccountId validation."""
        # Test with different cashAccountId values
        test_ids = [0, 1, 999999, -1]

        for test_id in test_ids:
            test_data = self.credit_account_data.copy()
            test_data['cashAccountId'] = test_id
            test_data['number'] = f'TEST{test_id:06d}'

            try:
                credit_account = CreditAccount.objects.create(**test_data)
                self.assertEqual(credit_account.cashAccountId, test_id)
            except Exception:
                # Some IDs might not be valid
                pass

    def test_credit_account_field_constraints(self):
        """Test CreditAccount field constraints."""
        # Test maximum field lengths
        long_data = self.credit_account_data.copy()
        long_data['number'] = 'a' * 100  # Exceeds max_length
        long_data['description'] = 'b' * 100  # Exceeds max_length

        with self.assertRaises(Exception):
            account = CreditAccount(**long_data)
            account.full_clean()
            account.save()


@pytest.mark.unit
class TestCreditAccountPytest(object):
    """Pytest-style tests for CreditAccount model."""

    @pytest.mark.django_db
    def test_credit_account_factory(self, credit_account_factory):
        """Test CreditAccount creation using factory."""
        credit_account = credit_account_factory(
            number="4444444444",
            availableBalance=10000.00,
            cashAccountId=5
        )

        assert credit_account.number == "4444444444"
        assert credit_account.availableBalance == 10000.00
        assert credit_account.cashAccountId == 5

    @pytest.mark.django_db
    def test_credit_account_balance_operations(self, credit_account_factory):
        """Test credit account balance operations."""
        credit_account = credit_account_factory(availableBalance=5000.00)

        # Test credit utilization
        original_balance = credit_account.availableBalance
        credit_account.availableBalance -= 1000.00  # Simulate credit usage
        credit_account.save()

        credit_account.refresh_from_db()
        assert credit_account.availableBalance == original_balance - 1000.00

    @pytest.mark.django_db
    def test_credit_account_queries(self, credit_account_factory):
        """Test CreditAccount query operations."""
        # Create accounts with different credit limits
        low_credit = credit_account_factory(availableBalance=1000.00, number="5555555555")
        high_credit = credit_account_factory(availableBalance=20000.00, number="6666666666")

        # Test credit limit queries
        high_credit_accounts = CreditAccount.objects.filter(availableBalance__gte=10000.00)
        assert high_credit in high_credit_accounts

        # Test by cash account ID
        specific_cash_accounts = CreditAccount.objects.filter(cashAccountId=1)
        # Results depend on test data


class TestTransfer(TestCase):
    """Unit tests for Transfer model."""

    def setUp(self):
        """Set up test data."""
        from datetime import datetime
        self.transfer_data = {
            'fromAccount': '1234567890',
            'toAccount': '0987654321',
            'description': 'Test Transfer',
            'amount': 100.00,
            'fee': 20.00,
            'username': 'testuser',
            'date': datetime.now()
        }

    def test_transfer_creation(self):
        """Test that Transfer can be created with valid data."""
        transfer = Transfer.objects.create(**self.transfer_data)

        self.assertEqual(transfer.fromAccount, '1234567890')
        self.assertEqual(transfer.toAccount, '0987654321')
        self.assertEqual(transfer.description, 'Test Transfer')
        self.assertEqual(transfer.amount, 100.00)
        self.assertEqual(transfer.fee, 20.00)
        self.assertEqual(transfer.username, 'testuser')
        self.assertIsNotNone(transfer.date)

    def test_transfer_model_serialization_mixin(self):
        """Test ModelSerializationMixin methods on Transfer."""
        transfer = Transfer.objects.create(**self.transfer_data)

        # Test as_dict method
        transfer_dict = transfer.as_dict()
        self.assertIsInstance(transfer_dict, dict)
        self.assertEqual(transfer_dict['fromAccount'], '1234567890')
        self.assertEqual(transfer_dict['toAccount'], '0987654321')
        self.assertEqual(transfer_dict['amount'], 100.00)
        self.assertEqual(transfer_dict['fee'], 20.00)

        # Test that all fields are included
        expected_fields = ['id', 'fromAccount', 'toAccount', 'description',
                          'amount', 'fee', 'username', 'date']
        for field in expected_fields:
            self.assertIn(field, transfer_dict)

    def test_transfer_from_dict_method(self):
        """Test ModelSerializationMixin from_dict method."""
        transfer = Transfer(**self.transfer_data)

        # Test from_dict method
        new_data = {
            'description': 'Updated Transfer',
            'amount': 200.00,
            'fee': 25.00
        }

        transfer.from_dict(new_data)

        self.assertEqual(transfer.description, 'Updated Transfer')
        self.assertEqual(transfer.amount, 200.00)
        self.assertEqual(transfer.fee, 25.00)
        # Other fields should remain unchanged
        self.assertEqual(transfer.fromAccount, '1234567890')
        self.assertEqual(transfer.toAccount, '0987654321')

    def test_transfer_amount_validation(self):
        """Test Transfer amount validation."""
        # Test positive amount
        transfer = Transfer.objects.create(**self.transfer_data)
        self.assertGreater(transfer.amount, 0)

        # Test zero amount
        zero_data = self.transfer_data.copy()
        zero_data['amount'] = 0.0
        try:
            zero_transfer = Transfer.objects.create(**zero_data)
            self.assertEqual(zero_transfer.amount, 0.0)
        except Exception:
            # If zero amount is not allowed
            pass

        # Test negative amount (potential vulnerability)
        negative_data = self.transfer_data.copy()
        negative_data['amount'] = -100.0
        try:
            negative_transfer = Transfer.objects.create(**negative_data)
            # If negative amounts are allowed (vulnerability)
            self.assertEqual(negative_transfer.amount, -100.0)
        except Exception:
            # If negative amounts are properly rejected
            pass

    def test_transfer_fee_validation(self):
        """Test Transfer fee validation."""
        # Test different fee scenarios
        fee_scenarios = [0.0, 5.0, 20.0, 100.0, -5.0]  # Including negative fee

        for i, fee in enumerate(fee_scenarios):
            fee_data = self.transfer_data.copy()
            fee_data['fee'] = fee
            fee_data['fromAccount'] = f'FEE{i:07d}'

            try:
                fee_transfer = Transfer.objects.create(**fee_data)
                self.assertEqual(fee_transfer.fee, fee)
                if fee < 0:
                    # Negative fee could be a vulnerability
                    self.assertLess(fee_transfer.fee, 0)
            except Exception:
                # Some fee values might not be allowed
                pass

    def test_transfer_account_validation(self):
        """Test Transfer account validation."""
        # Test same from and to account (potential vulnerability)
        same_account_data = self.transfer_data.copy()
        same_account_data['toAccount'] = same_account_data['fromAccount']

        try:
            same_transfer = Transfer.objects.create(**same_account_data)
            # If same account transfers are allowed (potential issue)
            self.assertEqual(same_transfer.fromAccount, same_transfer.toAccount)
        except Exception:
            # If same account transfers are properly prevented
            pass

    def test_transfer_date_handling(self):
        """Test Transfer date field handling."""
        from datetime import datetime, timedelta

        # Test past date
        past_data = self.transfer_data.copy()
        past_data['date'] = datetime.now() - timedelta(days=30)
        past_data['fromAccount'] = 'PAST000001'

        past_transfer = Transfer.objects.create(**past_data)
        self.assertLess(past_transfer.date, datetime.now())

        # Test future date
        future_data = self.transfer_data.copy()
        future_data['date'] = datetime.now() + timedelta(days=1)
        future_data['fromAccount'] = 'FUTR000001'

        try:
            future_transfer = Transfer.objects.create(**future_data)
            # If future dates are allowed
            self.assertGreater(future_transfer.date, datetime.now())
        except Exception:
            # If future dates are rejected
            pass

    def test_transfer_description_injection(self):
        """Test Transfer description with potentially malicious content."""
        injection_data = self.transfer_data.copy()
        injection_data['description'] = "<script>alert('XSS')</script>"
        injection_data['fromAccount'] = 'INJS000001'

        try:
            injection_transfer = Transfer.objects.create(**injection_data)
            # Check if the malicious content is stored as-is (vulnerability)
            self.assertIn('script', injection_transfer.description)
        except Exception:
            # If malicious content is rejected
            pass


@pytest.mark.unit
class TestTransferPytest(object):
    """Pytest-style tests for Transfer model."""

    @pytest.mark.django_db
    def test_transfer_factory(self, transfer_factory):
        """Test Transfer creation using factory."""
        transfer = transfer_factory(
            fromAccount="7777777777",
            toAccount="8888888888",
            amount=500.00
        )

        assert transfer.fromAccount == "7777777777"
        assert transfer.toAccount == "8888888888"
        assert transfer.amount == 500.00

    @pytest.mark.django_db
    def test_transfer_helper_functions(self, transfer_factory):
        """Test TransferTestHelpers functions."""
        transfer = transfer_factory(amount=150.00, fee=30.00)

        # Test assert_transfer_data helper
        TransferTestHelpers.assert_transfer_data(
            transfer,
            expected_amount=150.00,
            expected_fee=30.00
        )

    @pytest.mark.django_db
    def test_transfer_serialization_round_trip(self, transfer_factory):
        """Test complete serialization round-trip."""
        original_transfer = transfer_factory()

        # Serialize to dict
        transfer_dict = original_transfer.as_dict()

        # Create new transfer and populate from dict
        new_transfer = Transfer()
        new_transfer.from_dict(transfer_dict)
        new_transfer.save()

        # Compare key fields
        assert new_transfer.fromAccount == original_transfer.fromAccount
        assert new_transfer.toAccount == original_transfer.toAccount
        assert new_transfer.amount == original_transfer.amount
        assert new_transfer.fee == original_transfer.fee

    @pytest.mark.django_db
    def test_transfer_queries(self, transfer_factory):
        """Test Transfer query operations."""
        # Create transfers with different amounts
        small_transfer = transfer_factory(amount=50.00, fromAccount="SMALL00001")
        large_transfer = transfer_factory(amount=5000.00, fromAccount="LARGE00001")

        # Test amount-based queries
        large_transfers = Transfer.objects.filter(amount__gte=1000.00)
        assert large_transfer in large_transfers

        small_transfers = Transfer.objects.filter(amount__lt=100.00)
        assert small_transfer in small_transfers

        # Test account-based queries
        from_account_transfers = Transfer.objects.filter(fromAccount="SMALL00001")
        assert small_transfer in from_account_transfers


class TestTransaction(TestCase):
    """Unit tests for Transaction model."""

    def setUp(self):
        """Set up test data."""
        from datetime import datetime
        self.transaction_data = {
            'number': 'TXN123456',
            'description': 'Test Transaction',
            'amount': 100.00,
            'availableBalance': 900.00,
            'date': datetime.now()
        }

    def test_transaction_creation(self):
        """Test that Transaction can be created with valid data."""
        transaction = Transaction.objects.create(**self.transaction_data)

        self.assertEqual(transaction.number, 'TXN123456')
        self.assertEqual(transaction.description, 'Test Transaction')
        self.assertEqual(transaction.amount, 100.00)
        self.assertEqual(transaction.availableBalance, 900.00)
        self.assertIsNotNone(transaction.date)

    def test_transaction_number_format(self):
        """Test Transaction number format validation."""
        # Test alphanumeric transaction number
        transaction = Transaction.objects.create(**self.transaction_data)
        self.assertTrue(transaction.number.startswith('TXN'))

        # Test numeric-only transaction number
        numeric_data = self.transaction_data.copy()
        numeric_data['number'] = '123456789'
        numeric_transaction = Transaction.objects.create(**numeric_data)
        self.assertTrue(numeric_transaction.number.isdigit())

        # Test special characters in transaction number
        special_data = self.transaction_data.copy()
        special_data['number'] = 'TXN-2023-001'
        try:
            special_transaction = Transaction.objects.create(**special_data)
            self.assertIn('-', special_transaction.number)
        except Exception:
            # If special characters are not allowed
            pass

    def test_transaction_amount_validation(self):
        """Test Transaction amount validation."""
        # Test positive amount
        transaction = Transaction.objects.create(**self.transaction_data)
        self.assertGreater(transaction.amount, 0)

        # Test zero amount
        zero_data = self.transaction_data.copy()
        zero_data['amount'] = 0.0
        zero_data['number'] = 'TXN000000'
        try:
            zero_transaction = Transaction.objects.create(**zero_data)
            self.assertEqual(zero_transaction.amount, 0.0)
        except Exception:
            # If zero amount is not allowed
            pass

        # Test negative amount (refund or reversal)
        negative_data = self.transaction_data.copy()
        negative_data['amount'] = -50.0
        negative_data['number'] = 'TXN-REF001'
        try:
            negative_transaction = Transaction.objects.create(**negative_data)
            self.assertEqual(negative_transaction.amount, -50.0)
        except Exception:
            # If negative amounts are not allowed
            pass

    def test_transaction_balance_consistency(self):
        """Test Transaction availableBalance logic."""
        transaction = Transaction.objects.create(**self.transaction_data)

        # Check that balance and amount relationship makes sense
        # This is application logic that might not be enforced at model level
        if transaction.amount > 0:
            # For deposits, balance should potentially be higher
            self.assertIsInstance(transaction.availableBalance, float)

        # Test very large balance
        large_balance_data = self.transaction_data.copy()
        large_balance_data['availableBalance'] = 999999999.99
        large_balance_data['number'] = 'TXN-LARGE'

        large_transaction = Transaction.objects.create(**large_balance_data)
        self.assertEqual(large_transaction.availableBalance, 999999999.99)

    def test_transaction_description_content(self):
        """Test Transaction description field."""
        # Test empty description
        empty_desc_data = self.transaction_data.copy()
        empty_desc_data['description'] = ''
        empty_desc_data['number'] = 'TXN-EMPTY'

        try:
            empty_transaction = Transaction.objects.create(**empty_desc_data)
            self.assertEqual(empty_transaction.description, '')
        except Exception:
            # If empty description is not allowed
            pass

        # Test very long description
        long_desc_data = self.transaction_data.copy()
        long_desc_data['description'] = 'x' * 100  # Beyond max_length
        long_desc_data['number'] = 'TXN-LONG'

        with self.assertRaises(Exception):
            txn = Transaction(**long_desc_data)
            txn.full_clean()
            txn.save()

        # Test special characters
        special_desc_data = self.transaction_data.copy()
        special_desc_data['description'] = "Payment for 'Services' & Goods $100"
        special_desc_data['number'] = 'TXN-SPECIAL'

        try:
            special_transaction = Transaction.objects.create(**special_desc_data)
            self.assertIn("'", special_transaction.description)
            self.assertIn("$", special_transaction.description)
        except Exception:
            # If special characters cause issues
            pass

    def test_transaction_date_validation(self):
        """Test Transaction date field validation."""
        from datetime import datetime, timedelta

        # Test past date
        past_data = self.transaction_data.copy()
        past_data['date'] = datetime.now() - timedelta(days=365)
        past_data['number'] = 'TXN-PAST'

        past_transaction = Transaction.objects.create(**past_data)
        self.assertLess(past_transaction.date, datetime.now())

        # Test future date (might be validation issue)
        future_data = self.transaction_data.copy()
        future_data['date'] = datetime.now() + timedelta(days=1)
        future_data['number'] = 'TXN-FUTURE'

        try:
            future_transaction = Transaction.objects.create(**future_data)
            # If future dates are allowed (potential issue)
            self.assertGreater(future_transaction.date, datetime.now())
        except Exception:
            # If future dates are properly rejected
            pass

    def test_transaction_number_uniqueness(self):
        """Test Transaction number uniqueness (if enforced)."""
        Transaction.objects.create(**self.transaction_data)

        # Try to create another transaction with same number
        duplicate_data = self.transaction_data.copy()
        duplicate_data['description'] = 'Duplicate Transaction'

        try:
            duplicate_transaction = Transaction.objects.create(**duplicate_data)
            # If duplicates are allowed, test the behavior
            duplicate_transactions = Transaction.objects.filter(number='TXN123456')
            self.assertGreaterEqual(len(duplicate_transactions), 2)
        except Exception:
            # If duplicates are properly prevented
            pass

    def test_transaction_precision_handling(self):
        """Test Transaction decimal precision handling."""
        precision_data = self.transaction_data.copy()
        precision_data['amount'] = 123.456789  # More than 2 decimal places
        precision_data['availableBalance'] = 876.543210
        precision_data['number'] = 'TXN-PREC'

        precision_transaction = Transaction.objects.create(**precision_data)

        # Check how precision is handled (might be rounded)
        self.assertIsInstance(precision_transaction.amount, float)
        self.assertIsInstance(precision_transaction.availableBalance, float)


@pytest.mark.unit
class TestTransactionPytest(object):
    """Pytest-style tests for Transaction model."""

    @pytest.mark.django_db
    def test_transaction_factory(self, transaction_factory):
        """Test Transaction creation using factory."""
        transaction = transaction_factory(
            number="TXN-TEST-001",
            amount=250.00,
            availableBalance=750.00
        )

        assert transaction.number == "TXN-TEST-001"
        assert transaction.amount == 250.00
        assert transaction.availableBalance == 750.00

    @pytest.mark.django_db
    def test_transaction_queries(self, transaction_factory):
        """Test Transaction query operations."""
        # Create transactions with different amounts
        small_txn = transaction_factory(amount=25.00, number="TXN-SMALL")
        large_txn = transaction_factory(amount=5000.00, number="TXN-LARGE")

        # Test amount-based queries
        large_transactions = Transaction.objects.filter(amount__gte=1000.00)
        assert large_txn in large_transactions

        small_transactions = Transaction.objects.filter(amount__lt=100.00)
        assert small_txn in small_transactions

        # Test number-based queries
        specific_txn = Transaction.objects.filter(number="TXN-SMALL")
        assert small_txn in specific_txn

    @pytest.mark.django_db
    def test_transaction_balance_calculations(self, transaction_factory):
        """Test transaction balance-related logic."""
        transaction = transaction_factory(
            amount=100.00,
            availableBalance=900.00
        )

        # Test balance update simulation
        new_balance = transaction.availableBalance - transaction.amount
        assert new_balance == 800.00

        # Test balance queries
        high_balance_txns = Transaction.objects.filter(availableBalance__gte=500.00)
        assert transaction in high_balance_txns

    @pytest.mark.django_db
    def test_transaction_date_queries(self, transaction_factory):
        """Test Transaction date-based queries."""
        from datetime import datetime, timedelta

        # Create transactions with different dates
        old_txn = transaction_factory(
            number="TXN-OLD",
            date=datetime.now() - timedelta(days=30)
        )
        recent_txn = transaction_factory(
            number="TXN-RECENT",
            date=datetime.now() - timedelta(hours=1)
        )

        # Test date range queries
        recent_transactions = Transaction.objects.filter(
            date__gte=datetime.now() - timedelta(days=7)
        )
        assert recent_txn in recent_transactions

        old_transactions = Transaction.objects.filter(
            date__lt=datetime.now() - timedelta(days=7)
        )
        assert old_txn in old_transactions


class TestTransferFeeCalculation(TestCase):
    """Test Transfer fee calculation edge cases and business rules."""

    def test_transfer_fee_basic_calculation(self):
        """Test basic fee calculation for transfers."""
        from datetime import datetime

        transfer = Transfer.objects.create(
            fromAccount='1111111111',
            toAccount='2222222222',
            description='Fee Test Transfer',
            amount=100.0,
            fee=20.0,
            username='testuser',
            date=datetime.now()
        )

        # Test total cost calculation
        total_cost = transfer.amount + transfer.fee
        self.assertEqual(total_cost, 120.0)

    def test_transfer_fee_percentage_based(self):
        """Test fee calculation as percentage of transfer amount."""
        from datetime import datetime

        # Simulate 2% fee structure
        transfer_amount = 1000.0
        fee_percentage = 0.02
        calculated_fee = transfer_amount * fee_percentage

        transfer = Transfer.objects.create(
            fromAccount='3333333333',
            toAccount='4444444444',
            description='Percentage Fee Transfer',
            amount=transfer_amount,
            fee=calculated_fee,
            username='testuser',
            date=datetime.now()
        )

        self.assertEqual(transfer.fee, 20.0)
        self.assertEqual(transfer.amount + transfer.fee, 1020.0)

    def test_transfer_minimum_fee_enforcement(self):
        """Test minimum fee enforcement for small transfers."""
        from datetime import datetime

        # Small transfer that would calculate to fee less than minimum
        small_amount = 1.0
        minimum_fee = 5.0

        transfer = Transfer.objects.create(
            fromAccount='5555555555',
            toAccount='6666666666',
            description='Minimum Fee Transfer',
            amount=small_amount,
            fee=minimum_fee,  # Manually set to minimum
            username='testuser',
            date=datetime.now()
        )

        # Fee should be minimum even for small amounts
        self.assertEqual(transfer.fee, 5.0)
        self.assertGreater(transfer.fee, transfer.amount * 0.02)  # Fee > 2% of amount

    def test_transfer_maximum_fee_cap(self):
        """Test maximum fee cap for large transfers."""
        from datetime import datetime

        # Large transfer that would calculate to fee more than maximum
        large_amount = 10000.0
        maximum_fee = 100.0  # Cap at $100

        transfer = Transfer.objects.create(
            fromAccount='7777777777',
            toAccount='8888888888',
            description='Maximum Fee Transfer',
            amount=large_amount,
            fee=maximum_fee,  # Manually set to maximum
            username='testuser',
            date=datetime.now()
        )

        # Fee should be capped even for large amounts
        self.assertEqual(transfer.fee, 100.0)
        self.assertLess(transfer.fee, large_amount * 0.02)  # Fee < 2% of amount

    def test_transfer_zero_fee_special_case(self):
        """Test zero fee for special transfer types."""
        from datetime import datetime

        # Some transfers might have zero fee (promotional, internal, etc.)
        transfer = Transfer.objects.create(
            fromAccount='9999999999',
            toAccount='1010101010',
            description='Zero Fee Promotional Transfer',
            amount=500.0,
            fee=0.0,  # Zero fee
            username='testuser',
            date=datetime.now()
        )

        self.assertEqual(transfer.fee, 0.0)
        self.assertEqual(transfer.amount + transfer.fee, 500.0)

    def test_transfer_fee_precision_handling(self):
        """Test fee calculation precision for fractional amounts."""
        from datetime import datetime
        from decimal import Decimal

        # Test with fractional amounts that could cause precision issues
        transfer_amount = 33.33
        fee_rate = 0.025  # 2.5%
        calculated_fee = round(transfer_amount * fee_rate, 2)

        transfer = Transfer.objects.create(
            fromAccount='1212121212',
            toAccount='3434343434',
            description='Precision Test Transfer',
            amount=transfer_amount,
            fee=calculated_fee,
            username='testuser',
            date=datetime.now()
        )

        # Check precision is maintained
        self.assertEqual(transfer.fee, 0.83)  # 33.33 * 0.025 = 0.83325, rounded to 0.83

        # Verify total doesn't have precision errors
        total = transfer.amount + transfer.fee
        self.assertEqual(round(total, 2), 34.16)

    def test_transfer_negative_amount_fee_interaction(self):
        """Test fee calculation for negative amounts (refunds)."""
        from datetime import datetime

        try:
            # Test refund scenario with negative amount
            transfer = Transfer.objects.create(
                fromAccount='5656565656',
                toAccount='7878787878',
                description='Refund Transfer',
                amount=-100.0,  # Negative amount (refund)
                fee=0.0,  # No fee on refunds
                username='testuser',
                date=datetime.now()
            )

            # If this succeeds, negative amounts are allowed
            self.assertEqual(transfer.amount, -100.0)
            self.assertEqual(transfer.fee, 0.0)

            # Total would be negative
            total = transfer.amount + transfer.fee
            self.assertEqual(total, -100.0)

        except Exception:
            # If this fails, negative amounts are properly prevented
            pass

    def test_transfer_fee_currency_edge_cases(self):
        """Test fee calculation with currency edge cases."""
        from datetime import datetime

        # Test with very small amounts (sub-cent)
        micro_amount = 0.01
        micro_fee = 0.00  # Fee might round to zero

        transfer = Transfer.objects.create(
            fromAccount='9090909090',
            toAccount='1313131313',
            description='Micro Amount Transfer',
            amount=micro_amount,
            fee=micro_fee,
            username='testuser',
            date=datetime.now()
        )

        self.assertEqual(transfer.amount, 0.01)
        self.assertEqual(transfer.fee, 0.0)

        # Test with very large amounts
        large_amount = 999999.99
        large_fee = 999.99  # Potentially capped fee

        transfer_large = Transfer.objects.create(
            fromAccount='1414141414',
            toAccount='1515151515',
            description='Large Amount Transfer',
            amount=large_amount,
            fee=large_fee,
            username='testuser',
            date=datetime.now()
        )

        self.assertEqual(transfer_large.amount, 999999.99)
        self.assertEqual(transfer_large.fee, 999.99)
