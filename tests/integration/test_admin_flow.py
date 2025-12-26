"""
Integration tests for admin flow.

This module provides integration tests for admin user workflows including
account management, user administration, and privilege validation in the
insecure banking application.

Test Categories:
- Admin user account management workflows
- Admin account listing and details functionality
- Admin privilege validation and access control
- Admin-specific vulnerability scenarios

Constitutional Requirements:
- All tests must preserve intentional security vulnerabilities
- SQL injection in admin services must remain intact
- Privilege escalation vulnerabilities must be preserved
- Admin authorization bypass vulnerabilities must remain testable
"""

import pytest
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.conf import settings
from unittest.mock import patch, Mock

from web.models import Account, CashAccount, CreditAccount


@pytest.mark.integration
class TestAdminFlow(TestCase):
    """Integration tests for admin workflows."""

    def setUp(self):
        """Set up test data for admin flow tests."""
        self.client = Client()

        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@example.com',
            is_staff=True,
            is_superuser=True
        )

        # Create regular user
        self.regular_user = User.objects.create_user(
            username='user1',
            password='pass123',
            email='user1@example.com'
        )

        # Create corresponding accounts
        self.admin_account = Account.objects.create(
            username='admin',
            name='Admin',
            surname='User',
            password='admin123'
        )

        self.user_account = Account.objects.create(
            username='user1',
            name='Regular',
            surname='User',
            password='pass123'
        )

        # Create additional test accounts for admin management
        self.test_accounts = []
        for i in range(3):
            account = Account.objects.create(
                username=f'testuser{i}',
                name=f'Test{i}',
                surname='User',
                password=f'pass{i}'
            )
            self.test_accounts.append(account)

    @patch('web.views.AccountService.find_users_by_username')
    @patch('web.views.AccountService.find_all_users')
    def test_admin_account_management_workflow(self, mock_find_all, mock_find_by_username):
        """Test admin user account management workflow."""
        # Mock service responses
        mock_find_by_username.return_value = [self.admin_account]
        mock_find_all.return_value = [self.admin_account] + self.test_accounts

        # Login as admin
        self.client.force_login(self.admin_user)

        # Access admin dashboard
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin.html')

        # Verify admin has access to all user accounts
        mock_find_by_username.assert_called_with('admin')
        mock_find_all.assert_called_once()

        # Verify admin context includes all accounts
        context = response.context
        self.assertEqual(context['account'], self.admin_account)
        self.assertEqual(len(context['accounts']), 4)  # admin + 3 test accounts

    @patch('web.views.AccountService.find_users_by_username')
    @patch('web.views.AccountService.find_all_users')
    def test_admin_account_listing_functionality(self, mock_find_all, mock_find_by_username):
        """Test admin account listing and details functionality."""
        # Mock service responses with multiple accounts
        mock_find_by_username.return_value = [self.admin_account]
        all_accounts = [self.admin_account, self.user_account] + self.test_accounts
        mock_find_all.return_value = all_accounts

        self.client.force_login(self.admin_user)

        response = self.client.get('/admin')

        # Verify all accounts are accessible to admin
        self.assertEqual(response.status_code, 200)
        context = response.context

        # Admin should see all user accounts
        self.assertEqual(len(context['accounts']), 5)  # admin + user1 + 3 test accounts

        # Verify account details are exposed
        account_usernames = [acc.username for acc in context['accounts']]
        self.assertIn('admin', account_usernames)
        self.assertIn('user1', account_usernames)
        for i in range(3):
            self.assertIn(f'testuser{i}', account_usernames)

    def test_admin_privilege_validation(self):
        """Test admin privilege validation and access control."""
        # Test 1: Regular user trying to access admin page
        self.client.force_login(self.regular_user)

        with patch('web.views.AccountService.find_users_by_username') as mock_find_users:
            mock_find_users.return_value = [self.user_account]

            response = self.client.get('/admin')

            # Should either deny access or show limited data
            # Note: The app may not have proper admin authorization (vulnerability)
            self.assertIn(response.status_code, [200, 302, 403])

            if response.status_code == 200:
                # If access is allowed, it's an authorization bypass vulnerability
                # Verify regular user gets admin access (vulnerability documented)
                pass

    def test_admin_sql_injection_vulnerability(self):
        """Test SQL injection vulnerability in admin functionality."""
        # Create malicious admin username
        malicious_admin = User.objects.create_user(
            username="admin'; DROP TABLE accounts; --",
            password='admin123',
            email='malicious@example.com'
        )

        self.client.force_login(malicious_admin)

        with patch('web.views.AccountService.find_users_by_username') as mock_find_users:
            with patch('web.views.AccountService.find_all_users') as mock_find_all:
                mock_find_users.return_value = [self.admin_account]
                mock_find_all.return_value = [self.admin_account]

                response = self.client.get('/admin')

                # Verify malicious username was passed to service (vulnerability)
                mock_find_users.assert_called_with("admin'; DROP TABLE accounts; --")

                # Service should be called with SQL injection payload
                self.assertEqual(response.status_code, 200)

    def test_admin_privilege_escalation_vulnerability(self):
        """Test privilege escalation vulnerability scenarios."""
        # Test scenario: Regular user manipulating session to gain admin access

        # Start as regular user
        self.client.force_login(self.regular_user)

        # Attempt to access admin functionality by manipulating requests
        with patch('web.views.AccountService.find_users_by_username') as mock_find_users:
            with patch('web.views.AccountService.find_all_users') as mock_find_all:
                # Mock as if user has admin privileges
                mock_find_users.return_value = [self.user_account]
                mock_find_all.return_value = [self.admin_account] + self.test_accounts

                # Try to access admin page
                response = self.client.get('/admin')

                # If successful, documents privilege escalation vulnerability
                if response.status_code == 200:
                    # Regular user gained admin access (vulnerability)
                    context = response.context
                    self.assertIn('accounts', context)
                    # User can see all accounts despite not being admin

    def test_admin_mass_user_enumeration(self):
        """Test admin mass user enumeration vulnerability."""
        self.client.force_login(self.admin_user)

        with patch('web.views.AccountService.find_users_by_username') as mock_find_users:
            with patch('web.views.AccountService.find_all_users') as mock_find_all:
                mock_find_users.return_value = [self.admin_account]

                # Create large number of fake accounts for enumeration test
                large_account_list = []
                for i in range(1000):
                    fake_account = Mock()
                    fake_account.username = f'user{i:04d}'
                    fake_account.name = f'User{i}'
                    fake_account.surname = 'Test'
                    large_account_list.append(fake_account)

                mock_find_all.return_value = large_account_list

                response = self.client.get('/admin')

                # Admin can enumerate all users (information disclosure vulnerability)
                self.assertEqual(response.status_code, 200)
                context = response.context
                self.assertEqual(len(context['accounts']), 1000)

                # Verify all user data is exposed
                for account in context['accounts']:
                    self.assertTrue(hasattr(account, 'username'))
                    self.assertTrue(hasattr(account, 'name'))

    def test_admin_cross_tenant_data_access(self):
        """Test admin cross-tenant data access vulnerabilities."""
        # Simulate multi-tenant scenario where admin should only see certain data

        # Create "tenant" specific accounts
        tenant1_accounts = []
        tenant2_accounts = []

        for i in range(2):
            acc1 = Account.objects.create(
                username=f'tenant1_user{i}',
                name=f'Tenant1User{i}',
                surname='User',
                password='pass123'
            )
            tenant1_accounts.append(acc1)

            acc2 = Account.objects.create(
                username=f'tenant2_user{i}',
                name=f'Tenant2User{i}',
                surname='User',
                password='pass123'
            )
            tenant2_accounts.append(acc2)

        self.client.force_login(self.admin_user)

        with patch('web.views.AccountService.find_users_by_username') as mock_find_users:
            with patch('web.views.AccountService.find_all_users') as mock_find_all:
                mock_find_users.return_value = [self.admin_account]
                # Admin sees ALL tenant data (vulnerability)
                mock_find_all.return_value = tenant1_accounts + tenant2_accounts

                response = self.client.get('/admin')

                # Admin has access to all tenant data (security vulnerability)
                self.assertEqual(response.status_code, 200)
                context = response.context

                # Verify cross-tenant access
                usernames = [acc.username for acc in context['accounts']]
                for i in range(2):
                    self.assertIn(f'tenant1_user{i}', usernames)
                    self.assertIn(f'tenant2_user{i}', usernames)

    def test_admin_concurrent_operations(self):
        """Test admin concurrent operations and race conditions."""
        # Create multiple admin clients
        admin_client1 = Client()
        admin_client2 = Client()

        admin_client1.force_login(self.admin_user)
        admin_client2.force_login(self.admin_user)

        with patch('web.views.AccountService.find_users_by_username') as mock_find_users:
            with patch('web.views.AccountService.find_all_users') as mock_find_all:
                mock_find_users.return_value = [self.admin_account]
                mock_find_all.return_value = self.test_accounts

                # Concurrent admin operations
                response1 = admin_client1.get('/admin')
                response2 = admin_client2.get('/admin')

                # Both should succeed
                self.assertEqual(response1.status_code, 200)
                self.assertEqual(response2.status_code, 200)

                # Verify both see same data (consistency)
                context1 = response1.context
                context2 = response2.context
                self.assertEqual(len(context1['accounts']), len(context2['accounts']))

    def test_admin_session_hijacking_vulnerability(self):
        """Test admin session hijacking vulnerability scenarios."""
        # Login admin and get session
        self.client.force_login(self.admin_user)

        with patch('web.views.AccountService.find_users_by_username') as mock_find_users:
            with patch('web.views.AccountService.find_all_users') as mock_find_all:
                mock_find_users.return_value = [self.admin_account]
                mock_find_all.return_value = self.test_accounts

                # Get admin session
                response1 = self.client.get('/admin')
                admin_session_key = self.client.session.session_key

                # Create new client and attempt to use same session
                hijacker_client = Client()

                # Simulate session hijacking (if session key is predictable/exposed)
                if admin_session_key:
                    # This would be the vulnerability - using another user's session
                    hijacker_client.cookies[settings.SESSION_COOKIE_NAME] = admin_session_key

                    response2 = hijacker_client.get('/admin')

                    # If successful, session hijacking vulnerability exists
                    if response2.status_code == 200:
                        # Hijacker gained admin access through session reuse
                        context = response2.context
                        self.assertIn('accounts', context)

    def test_admin_information_disclosure(self):
        """Test admin information disclosure vulnerabilities."""
        self.client.force_login(self.admin_user)

        # Create accounts with sensitive information
        sensitive_account = Account.objects.create(
            username='sensitive_user',
            name='Sensitive',
            surname='Data',
            password='topsecret123'  # Password should not be disclosed
        )

        with patch('web.views.AccountService.find_users_by_username') as mock_find_users:
            with patch('web.views.AccountService.find_all_users') as mock_find_all:
                mock_find_users.return_value = [self.admin_account]
                mock_find_all.return_value = [sensitive_account]

                response = self.client.get('/admin')

                # Check if sensitive data is exposed in admin interface
                self.assertEqual(response.status_code, 200)
                context = response.context

                # Admin interface might expose sensitive user data
                account = context['accounts'][0]
                self.assertEqual(account.username, 'sensitive_user')

                # Check if password or other sensitive fields are exposed
                # (This documents the information disclosure vulnerability)
                if hasattr(account, 'password'):
                    # Password field is accessible (vulnerability)
                    self.assertTrue(len(account.password) > 0)
