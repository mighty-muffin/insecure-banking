"""
Integration tests for transfer flow.

This module provides integration tests for complete money transfer workflows
including transfer creation, validation, confirmation, and database updates
in the insecure banking application.

Test Categories:
- Complete money transfer process with database verification
- Insufficient balance handling and error cases
- Transfer validation and fee calculation
- Cross-account transaction integrity

Constitutional Requirements:
- All tests must preserve intentional security vulnerabilities
- SQL injection in transfer services must remain intact
- Command injection in transfer logging must be preserved
- Transfer validation bypass vulnerabilities must remain testable
"""

import json
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch, Mock

import pytest
from django.contrib.auth.models import User
from django.test import TestCase, Client

from web.models import Account, CashAccount, Transfer, Transaction


@pytest.mark.integration
class TestTransferFlow(TestCase):
    """Integration tests for transfer workflows."""

    def setUp(self):
        """Set up test data for transfer flow tests."""
        self.client = Client()

        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123',
            email='user1@example.com'
        )

        self.user2 = User.objects.create_user(
            username='user2',
            password='pass123',
            email='user2@example.com'
        )

        # Create corresponding accounts
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

    @patch('web.views.AccountService.find_users_by_username')
    @patch('web.views.CashAccountService.find_cash_accounts_by_username')
    @patch('web.views.TransferService.createNewTransfer')
    @patch('web.views.to_traces')
    def test_complete_transfer_process(self, mock_to_traces, mock_create_transfer,
                                       mock_find_cash, mock_find_users):
        """Test complete money transfer process with database verification."""
        # Mock service responses
        mock_find_users.return_value = [self.account1]
        mock_find_cash.return_value = [self.cash_account1]
        mock_create_transfer.return_value = None  # Simulate successful transfer
        mock_to_traces.return_value = "0"  # Simulate successful command execution

        # Login user
        self.client.force_login(self.user1)

        # Step 1: Access transfer page
        response = self.client.get('/transfer')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newTransfer.html')

        # Verify accountType cookie is set
        self.assertEqual(response.cookies['accountType'].value, 'Personal')

        # Step 2: Submit transfer form
        transfer_data = {
            'fromAccount': '1111111111',
            'toAccount': '2222222222',
            'description': 'Test Transfer',
            'amount': 100.00,
            'fee': 2.0  # 2% fee
        }

        response = self.client.post('/transfer', transfer_data)

        # For Personal account type, should redirect to transfer check
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transferCheck.html')

        # Verify session contains pending transfer
        self.assertIn('pendingTransfer', self.client.session)

        # Verify command injection vulnerability is exercised
        mock_to_traces.assert_called_once()
        call_args = mock_to_traces.call_args[0][0]
        self.assertIn('1111111111', call_args)
        self.assertIn('2222222222', call_args)
        self.assertIn('Personal', call_args)

        # Step 3: Confirm transfer
        response = self.client.post('/transfer/confirm', {
            'action': 'confirm'
        })

        # Should complete transfer and show confirmation
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transferConfirmation.html')

        # Verify transfer was created
        mock_create_transfer.assert_called_once()
        created_transfer = mock_create_transfer.call_args[0][0]
        self.assertEqual(created_transfer.fromAccount, '1111111111')
        self.assertEqual(created_transfer.toAccount, '2222222222')
        self.assertEqual(created_transfer.amount, 100.00)
        self.assertEqual(created_transfer.username, 'user1')

    @patch('web.views.AccountService.find_users_by_username')
    @patch('web.views.CashAccountService.find_cash_accounts_by_username')
    def test_insufficient_balance_handling(self, mock_find_cash, mock_find_users):
        """Test transfer with insufficient balance."""
        # Set up account with low balance
        low_balance_account = CashAccount.objects.create(
            number='3333333333',
            username='user1',
            description='Low Balance Account',
            availableBalance=50.00  # Less than transfer amount
        )

        mock_find_users.return_value = [self.account1]
        mock_find_cash.return_value = [low_balance_account]

        self.client.force_login(self.user1)

        # Attempt transfer larger than balance
        transfer_data = {
            'fromAccount': '3333333333',
            'toAccount': '2222222222',
            'description': 'Overdraft Test',
            'amount': 100.00,  # More than available balance
            'fee': 2.0
        }

        with patch('web.views.to_traces') as mock_to_traces:
            mock_to_traces.return_value = "0"

            self.client.cookies['accountType'] = 'Personal'
            response = self.client.post('/transfer', transfer_data)

            # Should proceed to check page (vulnerability - no balance validation)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'transferCheck.html')

    def test_transfer_validation_bypass(self):
        """Test transfer validation bypass vulnerabilities."""
        self.client.force_login(self.user1)

        # Test with zero amount
        with patch('web.views.AccountService.find_users_by_username') as mock_find_users:
            with patch('web.views.CashAccountService.find_cash_accounts_by_username') as mock_find_cash:
                mock_find_users.return_value = [self.account1]
                mock_find_cash.return_value = [self.cash_account1]

                transfer_data = {
                    'fromAccount': '1111111111',
                    'toAccount': '2222222222',
                    'description': 'Zero Amount Transfer',
                    'amount': 0.0,  # Zero amount
                    'fee': 2.0
                }

                with patch('web.views.to_traces') as mock_to_traces:
                    mock_to_traces.return_value = "0"

                    response = self.client.post('/transfer', transfer_data)

                    # Should proceed to check (validation bypass vulnerability)
                    self.assertEqual(response.status_code, 200)

    def test_transfer_fee_calculation_integration(self):
        """Test transfer fee calculation in complete workflow."""
        self.client.force_login(self.user1)

        with patch('web.views.AccountService.find_users_by_username') as mock_find_users:
            with patch('web.views.CashAccountService.find_cash_accounts_by_username') as mock_find_cash:
                with patch('web.views.TransferService.createNewTransfer') as mock_create:
                    mock_find_users.return_value = [self.account1]
                    mock_find_cash.return_value = [self.cash_account1]

                    # Submit transfer with percentage fee
                    transfer_data = {
                        'fromAccount': '1111111111',
                        'toAccount': '2222222222',
                        'description': 'Fee Calculation Test',
                        'amount': 200.00,
                        'fee': 2.5  # 2.5% fee
                    }

                    with patch('web.views.to_traces'):
                        # Submit and confirm transfer
                        self.client.post('/transfer', transfer_data)
                        response = self.client.post('/transfer/confirm', {'action': 'confirm'})

                        # Verify fee was calculated correctly
                        mock_create.assert_called_once()
                        transfer = mock_create.call_args[0][0]

                        # Fee should be (200.00 * 2.5) / 100 = 5.00
                        expected_fee = round((200.00 * 2.5) / 100, 2)
                        self.assertEqual(transfer.fee, expected_fee)
                        self.assertEqual(transfer.amount, 200.00)

    def test_transfer_sql_injection_vulnerability(self):
        """Test SQL injection vulnerability in transfer process."""
        self.client.force_login(self.user1)

        with patch('web.views.AccountService.find_users_by_username') as mock_find_users:
            with patch('web.views.CashAccountService.find_cash_accounts_by_username') as mock_find_cash:
                mock_find_users.return_value = [self.account1]
                mock_find_cash.return_value = [self.cash_account1]

                # Malicious SQL injection in account numbers
                transfer_data = {
                    'fromAccount': "1111111111'; DROP TABLE transfers; --",
                    'toAccount': "2222222222'; SELECT * FROM accounts; --",
                    'description': 'SQL Injection Test',
                    'amount': 100.00,
                    'fee': 2.0
                }

                with patch('web.views.to_traces') as mock_to_traces:
                    mock_to_traces.return_value = "0"

                    self.client.cookies['accountType'] = 'Personal'
                    response = self.client.post('/transfer', transfer_data)

                    # The vulnerable code should process malicious input
                    self.assertEqual(response.status_code, 200)

                    # Verify malicious input was passed to services
                    self.assertIn('pendingTransfer', self.client.session)
                    pending_transfer = json.loads(self.client.session['pendingTransfer'])
                    self.assertIn("DROP TABLE", pending_transfer['fromAccount'])

    def test_command_injection_in_transfer_logging(self):
        """Test command injection vulnerability in transfer logging."""
        self.client.force_login(self.user1)

        with patch('web.views.AccountService.find_users_by_username') as mock_find_users:
            with patch('web.views.CashAccountService.find_cash_accounts_by_username') as mock_find_cash:
                mock_find_users.return_value = [self.account1]
                mock_find_cash.return_value = [self.cash_account1]

                # Malicious command injection in account fields
                transfer_data = {
                    'fromAccount': '1111111111; rm -rf /',
                    'toAccount': '2222222222; cat /etc/passwd',
                    'description': 'Command Injection Test',
                    'amount': 100.00,
                    'fee': 2.0
                }

                with patch('web.views.to_traces') as mock_to_traces:
                    mock_to_traces.return_value = "0"

                    self.client.cookies['accountType'] = 'Personal'
                    response = self.client.post('/transfer', transfer_data)

                    # Verify command injection attempt was passed through
                    mock_to_traces.assert_called_once()
                    command = mock_to_traces.call_args[0][0]
                    self.assertIn('rm -rf /', command)
                    self.assertIn('cat /etc/passwd', command)

    def test_transfer_session_manipulation(self):
        """Test transfer session manipulation vulnerabilities."""
        self.client.force_login(self.user1)

        with patch('web.views.AccountService.find_users_by_username') as mock_find_users:
            with patch('web.views.CashAccountService.find_cash_accounts_by_username') as mock_find_cash:
                mock_find_users.return_value = [self.account1]
                mock_find_cash.return_value = [self.cash_account1]

                # Step 1: Create pending transfer
                transfer_data = {
                    'fromAccount': '1111111111',
                    'toAccount': '2222222222',
                    'description': 'Session Test',
                    'amount': 100.00,
                    'fee': 2.0
                }

                with patch('web.views.to_traces'):
                    self.client.cookies['accountType'] = 'Personal'
                    self.client.post('/transfer', transfer_data)

                # Step 2: Manually manipulate session data
                session = self.client.session
                pending_transfer = json.loads(session['pendingTransfer'])

                # Maliciously modify transfer amount
                pending_transfer['amount'] = 999999.99
                session['pendingTransfer'] = json.dumps(pending_transfer)
                session.save()

                # Step 3: Confirm manipulated transfer
                with patch('web.views.TransferService.createNewTransfer') as mock_create:
                    response = self.client.post('/transfer/confirm', {'action': 'confirm'})

                    # Verify manipulated amount was used (vulnerability)
                    if mock_create.called:
                        transfer = mock_create.call_args[0][0]
                        self.assertEqual(transfer.amount, 999999.99)

    def test_cross_user_transfer_authorization(self):
        """Test cross-user transfer authorization vulnerabilities."""
        # Login as user1 but try to transfer from user2's account
        self.client.force_login(self.user1)

        with patch('web.views.AccountService.find_users_by_username') as mock_find_users:
            with patch('web.views.CashAccountService.find_cash_accounts_by_username') as mock_find_cash:
                # Mock returns user1's data (logged in user)
                mock_find_users.return_value = [self.account1]
                mock_find_cash.return_value = [self.cash_account1]

                # Try to transfer from user2's account (authorization bypass)
                transfer_data = {
                    'fromAccount': '2222222222',  # User2's account
                    'toAccount': '1111111111',    # User1's account
                    'description': 'Unauthorized Transfer',
                    'amount': 500.00,
                    'fee': 2.0
                }

                with patch('web.views.to_traces'):
                    self.client.cookies['accountType'] = 'Personal'
                    response = self.client.post('/transfer', transfer_data)

                    # Should proceed without authorization check (vulnerability)
                    self.assertEqual(response.status_code, 200)
                    self.assertIn('pendingTransfer', self.client.session)

    def test_concurrent_transfer_handling(self):
        """Test concurrent transfer handling and race conditions."""
        # Create multiple clients for same user
        client1 = Client()
        client2 = Client()

        client1.force_login(self.user1)
        client2.force_login(self.user1)

        with patch('web.views.AccountService.find_users_by_username') as mock_find_users:
            with patch('web.views.CashAccountService.find_cash_accounts_by_username') as mock_find_cash:
                mock_find_users.return_value = [self.account1]
                mock_find_cash.return_value = [self.cash_account1]

                # Submit simultaneous transfers
                transfer_data = {
                    'fromAccount': '1111111111',
                    'toAccount': '2222222222',
                    'description': 'Concurrent Transfer',
                    'amount': 600.00,  # More than half the balance
                    'fee': 2.0
                }

                with patch('web.views.to_traces'):
                    response1 = client1.post('/transfer', transfer_data)
                    response2 = client2.post('/transfer', transfer_data)

                    # Both transfers might be allowed (race condition vulnerability)
                    self.assertEqual(response1.status_code, 200)
                    self.assertEqual(response2.status_code, 200)
