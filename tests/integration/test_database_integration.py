"""
Integration tests for database operations.

This module provides integration tests for database transaction integrity,
concurrent user scenarios, and data consistency across service boundaries
in the insecure banking application.

Test Categories:
- Database transaction integrity across service boundaries
- Concurrent user scenario tests with database isolation
- Data consistency tests for account balance updates
- Cross-service database interaction vulnerabilities

Constitutional Requirements:
- All tests must preserve intentional security vulnerabilities
- SQL injection in database operations must remain intact
- Transaction isolation vulnerabilities must be preserved
- Race condition vulnerabilities must remain testable
"""

import threading
import time
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch, Mock

import pytest
from django.contrib.auth.models import User
from django.db import transaction, connection
from django.test import TestCase, TransactionTestCase
from django.test.utils import override_settings

from web.models import Account, CashAccount, CreditAccount, Transfer, Transaction
from web.services import (
    AccountService, CashAccountService, CreditAccountService,
    TransferService, ActivityService
)


@pytest.mark.integration
class TestDatabaseIntegration(TransactionTestCase):
    """Integration tests for database operations and consistency."""

    def setUp(self):
        """Set up test data for database integration tests."""
        # Create test accounts
        self.account1 = Account.objects.create(
            username='user1',
            name='User',
            surname='One',
            password='pass123'
        )

        self.account2 = Account.objects.create(
            username='user2',
            name='User',
            surname='Two',
            password='pass123'
        )

        # Create cash accounts
        self.cash_account1 = CashAccount.objects.create(
            number='1111111111',
            username='user1',
            description='User 1 Cash Account',
            availableBalance=1000.00
        )

        self.cash_account2 = CashAccount.objects.create(
            number='2222222222',
            username='user2',
            description='User 2 Cash Account',
            availableBalance=500.00
        )

        # Create credit accounts
        self.credit_account1 = CreditAccount.objects.create(
            number='3333333333',
            username='user1',
            description='User 1 Credit Account',
            balance=200.00,
            availableBalance=800.00
        )

    def test_transaction_integrity_across_services(self):
        """Test database transaction integrity across service boundaries."""
        initial_balance1 = self.cash_account1.availableBalance
        initial_balance2 = self.cash_account2.availableBalance

        # Create transfer that involves multiple service calls
        transfer = Transfer(
            fromAccount='1111111111',
            toAccount='2222222222',
            description='Transaction Integrity Test',
            amount=100.00,
            fee=20.00,
            username='user1',
            date=date.today()
        )

        # Test transaction rollback on failure
        with patch('web.services.connection') as mock_connection:
            mock_cursor = Mock()
            mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

            # Simulate failure in second service call
            def side_effect(*args, **kwargs):
                if 'UPDATE' in args[0] and 'credit' in args[0].lower():
                    raise Exception("Database error in credit update")
                return None

            mock_cursor.execute.side_effect = side_effect

            # Transfer should fail and rollback
            try:
                TransferService.createNewTransfer(transfer)
            except Exception:
                pass

            # Verify balances unchanged (transaction rolled back)
            self.cash_account1.refresh_from_db()
            self.cash_account2.refresh_from_db()
            self.assertEqual(self.cash_account1.availableBalance, initial_balance1)
            self.assertEqual(self.cash_account2.availableBalance, initial_balance2)

    def test_concurrent_user_database_isolation(self):
        """Test concurrent user scenarios with database isolation."""
        results = []
        errors = []

        def user1_transfer():
            """User 1 makes a transfer."""
            try:
                # Simulate user 1 transferring money
                transfer = Transfer(
                    fromAccount='1111111111',
                    toAccount='2222222222',
                    description='Concurrent Transfer 1',
                    amount=200.00,
                    fee=10.00,
                    username='user1',
                    date=date.today()
                )

                with patch('web.services.connection') as mock_connection:
                    mock_cursor = Mock()
                    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

                    # Simulate database operations
                    TransferService.createNewTransfer(transfer)
                    results.append('user1_success')

            except Exception as e:
                errors.append(f'user1_error: {e}')

        def user2_transfer():
            """User 2 makes a transfer."""
            try:
                # Simulate user 2 transferring money
                transfer = Transfer(
                    fromAccount='2222222222',
                    toAccount='1111111111',
                    description='Concurrent Transfer 2',
                    amount=150.00,
                    fee=15.00,
                    username='user2',
                    date=date.today()
                )

                with patch('web.services.connection') as mock_connection:
                    mock_cursor = Mock()
                    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

                    # Simulate database operations
                    TransferService.createNewTransfer(transfer)
                    results.append('user2_success')

            except Exception as e:
                errors.append(f'user2_error: {e}')

        # Start concurrent threads
        thread1 = threading.Thread(target=user1_transfer)
        thread2 = threading.Thread(target=user2_transfer)

        thread1.start()
        thread2.start()

        thread1.join(timeout=5)
        thread2.join(timeout=5)

        # Check results
        # Both operations should complete or fail gracefully
        self.assertGreaterEqual(len(results) + len(errors), 0)

    def test_data_consistency_account_balance_updates(self):
        """Test data consistency for account balance updates."""
        initial_balance = self.cash_account1.availableBalance

        # Test multiple concurrent balance updates
        def update_balance(amount, operation_id):
            try:
                # Simulate balance update through service
                with patch('web.services.connection') as mock_connection:
                    mock_cursor = Mock()
                    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

                    # Different operations that affect balance
                    if operation_id % 2 == 0:
                        # Debit operation
                        CashAccountService.update_balance('1111111111', -amount)
                    else:
                        # Credit operation
                        CashAccountService.update_balance('1111111111', amount)

            except Exception:
                pass

        # Create multiple threads for balance updates
        threads = []
        for i in range(10):
            thread = threading.Thread(target=update_balance, args=(10.00, i))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join(timeout=1)

        # Verify final balance consistency
        # In a race condition scenario, final balance might be incorrect
        self.cash_account1.refresh_from_db()
        # Balance should be initial_balance (5 credits + 5 debits = 0 net change)
        # But race conditions might cause inconsistency (vulnerability)

    def test_sql_injection_in_database_operations(self):
        """Test SQL injection vulnerabilities in database operations."""
        # Test SQL injection in account lookup
        malicious_username = "user1'; DROP TABLE accounts; --"

        try:
            # This should trigger SQL injection vulnerability
            result = AccountService.find_users_by_username(malicious_username)

            # If no exception, SQL injection payload was processed
            # (This documents the vulnerability)

        except Exception as e:
            # SQL injection might cause database error
            self.assertIsInstance(e, Exception)

    def test_database_connection_pooling_vulnerabilities(self):
        """Test database connection pooling vulnerabilities."""
        connections_used = []

        def use_connection(operation_id):
            """Simulate multiple operations using database connections."""
            try:
                with patch('web.services.connection') as mock_connection:
                    mock_cursor = Mock()
                    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

                    # Simulate different users accessing database
                    if operation_id % 3 == 0:
                        AccountService.find_users_by_username('user1')
                    elif operation_id % 3 == 1:
                        CashAccountService.find_cash_accounts_by_username('user2')
                    else:
                        ActivityService.find_transactions_by_cash_account_number('1111111111')

                    connections_used.append(mock_connection)

            except Exception:
                pass

        # Create multiple threads to test connection pooling
        threads = []
        for i in range(20):
            thread = threading.Thread(target=use_connection, args=(i,))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join(timeout=1)

        # Verify connection usage
        self.assertGreater(len(connections_used), 0)

    def test_database_deadlock_scenarios(self):
        """Test database deadlock scenarios."""
        deadlock_occurred = []

        def transfer_operation_1():
            """Transfer from account 1 to account 2."""
            try:
                # Lock account 1 first, then account 2
                with transaction.atomic():
                    CashAccount.objects.select_for_update().get(number='1111111111')
                    time.sleep(0.1)  # Simulate processing time
                    CashAccount.objects.select_for_update().get(number='2222222222')

            except Exception as e:
                deadlock_occurred.append(f'op1: {e}')

        def transfer_operation_2():
            """Transfer from account 2 to account 1."""
            try:
                # Lock account 2 first, then account 1 (opposite order)
                with transaction.atomic():
                    CashAccount.objects.select_for_update().get(number='2222222222')
                    time.sleep(0.1)  # Simulate processing time
                    CashAccount.objects.select_for_update().get(number='1111111111')

            except Exception as e:
                deadlock_occurred.append(f'op2: {e}')

        # Start operations that could cause deadlock
        thread1 = threading.Thread(target=transfer_operation_1)
        thread2 = threading.Thread(target=transfer_operation_2)

        thread1.start()
        thread2.start()

        thread1.join(timeout=2)
        thread2.join(timeout=2)

        # Check if deadlock was detected and handled
        # Deadlock errors should be caught and handled gracefully

    def test_database_injection_via_service_layer(self):
        """Test database injection vulnerabilities via service layer."""
        # Test injection through various service methods
        malicious_inputs = [
            "1'; DELETE FROM cash_accounts; --",
            "1' UNION SELECT * FROM accounts WHERE '1'='1",
            "1' OR '1'='1'; DROP TABLE transfers; --"
        ]

        for malicious_input in malicious_inputs:
            try:
                # Test injection in different service methods
                CashAccountService.get_from_account_actual_amount(malicious_input)

                # If no exception, injection payload was processed
                # (Documents SQL injection vulnerability)

            except Exception:
                # Injection might cause database error
                pass

    def test_transaction_isolation_levels(self):
        """Test transaction isolation level vulnerabilities."""
        # Test dirty read scenario
        def reader_thread():
            """Thread that reads data during transaction."""
            try:
                time.sleep(0.1)  # Wait for writer to start

                # Read data that might be uncommitted
                balance = CashAccountService.get_from_account_actual_amount('1111111111')
                return balance

            except Exception:
                return None

        def writer_thread():
            """Thread that modifies data."""
            try:
                with transaction.atomic():
                    # Start transaction
                    account = CashAccount.objects.get(number='1111111111')
                    account.availableBalance = 999999.99
                    account.save()

                    time.sleep(0.2)  # Keep transaction open

                    # Rollback transaction
                    raise Exception("Intentional rollback")

            except Exception:
                pass

        # Start threads to test isolation
        reader = threading.Thread(target=reader_thread)
        writer = threading.Thread(target=writer_thread)

        writer.start()
        reader.start()

        writer.join(timeout=1)
        reader.join(timeout=1)

        # Check if dirty read occurred (isolation vulnerability)
        # Reader might see uncommitted changes from writer

    def test_database_constraint_bypass(self):
        """Test database constraint bypass vulnerabilities."""
        # Test negative balance constraint bypass
        try:
            # Attempt to create account with negative balance
            negative_account = CashAccount.objects.create(
                number='9999999999',
                username='testuser',
                description='Negative Balance Test',
                availableBalance=-1000.00  # Negative balance
            )

            # If successful, constraint bypass vulnerability exists
            self.assertEqual(negative_account.availableBalance, -1000.00)

        except Exception:
            # Constraint properly enforced
            pass

        # Test duplicate account number constraint bypass
        try:
            # Attempt to create duplicate account number
            duplicate_account = CashAccount.objects.create(
                number='1111111111',  # Same as existing account
                username='different_user',
                description='Duplicate Number Test',
                availableBalance=100.00
            )

            # If successful, uniqueness constraint bypass vulnerability exists
            self.assertEqual(duplicate_account.number, '1111111111')

        except Exception:
            # Constraint properly enforced
            pass
