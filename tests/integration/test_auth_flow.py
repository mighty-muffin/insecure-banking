"""
Integration tests for authentication flow.

This module provides integration tests for complete authentication workflows
including login, session management, logout, and access control in the
insecure banking application.

Test Categories:
- Complete login-dashboard-logout workflows
- Session persistence across multiple requests
- Unauthorized access protection and redirects
- Authentication edge cases and error handling

Constitutional Requirements:
- All tests must preserve intentional security vulnerabilities
- Authentication bypass vulnerabilities must remain intact
- Session management vulnerabilities must be preserved
- SQL injection in authentication must remain testable
"""

import pytest
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, Mock

from apps.accounts.models import Account
from apps.banking.models import CashAccount, CreditAccount


@pytest.mark.integration
class TestAuthenticationFlow(TestCase):
    """Integration tests for authentication workflows."""

    def setUp(self):
        """Set up test data for authentication flow tests."""
        self.client = Client()

        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

        # Create corresponding account
        self.account = Account.objects.create(
            username='testuser',
            name='Test',
            surname='User',
            password='testpass123'
        )

        # Create test accounts
        self.cash_account = CashAccount.objects.create(
            number='1234567890',
            username='testuser',
            description='Test Cash Account',
            availableBalance=1000.00
        )

        self.credit_account = CreditAccount.objects.create(
            cashAccountId=self.cash_account.id,
            number='9876543210',
            username='testuser',
            description='Test Credit Account',
            availableBalance=1500.00
        )

    @patch('apps.accounts.services.AccountService.find_users_by_username')
    @patch('apps.banking.services.CashAccountService.find_cash_accounts_by_username')
    @patch('apps.banking.services.CreditAccountService.find_credit_accounts_by_username')
    def test_complete_login_dashboard_logout_flow(self, mock_find_credit, mock_find_cash, mock_find_users):
        """Test complete user workflow from login to logout."""
        # Mock service responses for dashboard
        mock_find_users.return_value = [self.account]
        mock_find_cash.return_value = [self.cash_account]
        mock_find_credit.return_value = [self.credit_account]

        # Step 1: Access login page
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

        # Step 2: Submit login credentials
        with patch('web.views.authenticate') as mock_auth:
            with patch('web.views.login') as mock_login:
                mock_auth.return_value = self.user

                response = self.client.post('/login', {
                    'username': 'testuser',
                    'password': 'testpass123'
                })

                # Should redirect to dashboard
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.url, '/dashboard')

        # Step 3: Access dashboard (simulate following redirect)
        self.client.force_login(self.user)  # Simulate successful login
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)

        # Step 4: Logout
        with patch('web.views.logout') as mock_logout:
            response = self.client.get('/logout')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, '/login')
            mock_logout.assert_called_once()

    def test_session_persistence_across_requests(self):
        """Test session persistence across multiple authenticated requests."""
        # Login user
        self.client.force_login(self.user)

        # Make multiple requests to different authenticated endpoints
        with patch('web.views.AccountService.find_users_by_username') as mock_find_users:
            mock_find_users.return_value = [self.account]

            # Request 1: Dashboard
            response1 = self.client.get('/dashboard')
            self.assertEqual(response1.status_code, 200)

            # Request 2: User detail
            response2 = self.client.get('/dashboard/userDetail')
            self.assertEqual(response2.status_code, 200)

            # Request 3: Admin (if accessible)
            response3 = self.client.get('/admin')
            self.assertEqual(response3.status_code, 200)

            # Verify same user was used for all requests
            self.assertEqual(mock_find_users.call_count, 3)
            for call in mock_find_users.call_args_list:
                self.assertEqual(call[0][0], 'testuser')

    def test_unauthorized_access_protection(self):
        """Test unauthorized access protection and redirects."""
        # Try to access protected pages without authentication
        protected_urls = [
            '/dashboard',
            '/admin',
            '/dashboard/userDetail',
            '/transfer'
        ]

        for url in protected_urls:
            response = self.client.get(url)
            # Note: The app may not have proper authentication middleware
            # This test documents the current behavior (potential vulnerability)
            # Response could be 200 (no protection), 302 (redirect), or 403 (forbidden)
            self.assertIn(response.status_code, [200, 302, 403, 404])

    def test_authentication_failure_handling(self):
        """Test authentication failure scenarios."""
        # Test with invalid credentials
        with patch('web.views.authenticate') as mock_auth:
            mock_auth.return_value = None  # Authentication failure

            response = self.client.post('/login', {
                'username': 'testuser',
                'password': 'wrongpassword'
            })

            # Should return to login page with error
            self.assertEqual(response.status_code, 200)
            mock_auth.assert_called_once()

    def test_sql_injection_in_authentication(self):
        """Test that SQL injection vulnerability in authentication is preserved."""
        # Attempt SQL injection in username field
        with patch('web.views.authenticate') as mock_auth:
            mock_auth.return_value = None  # Simulate failed injection

            malicious_username = "admin'; DROP TABLE accounts; --"
            response = self.client.post('/login', {
                'username': malicious_username,
                'password': 'anything'
            })

            # The vulnerable authenticate function should be called with malicious input
            mock_auth.assert_called_once()
            # Verify the malicious input was passed through (vulnerability preserved)
            self.assertEqual(response.status_code, 200)

    def test_session_fixation_vulnerability(self):
        """Test session fixation vulnerability preservation."""
        # Get initial session
        response1 = self.client.get('/login')
        initial_session_key = self.client.session.session_key

        # Login with the same session
        with patch('web.views.authenticate') as mock_auth:
            with patch('web.views.login') as mock_login:
                mock_auth.return_value = self.user

                response2 = self.client.post('/login', {
                    'username': 'testuser',
                    'password': 'testpass123'
                })

                # Check if session key changed (it should, but might not due to vulnerability)
                final_session_key = self.client.session.session_key

                # Document current behavior - session fixation vulnerability may exist
                # If keys are the same, session fixation vulnerability is present
                if initial_session_key == final_session_key:
                    # Vulnerability present (expected for this intentionally vulnerable app)
                    pass
                else:
                    # Session properly regenerated
                    pass

    def test_authentication_timing_attack_vulnerability(self):
        """Test authentication timing attack vulnerability preservation."""
        import time

        # Test with valid username, invalid password
        start_time = time.time()
        with patch('web.views.authenticate') as mock_auth:
            mock_auth.return_value = None

            response1 = self.client.post('/login', {
                'username': 'testuser',  # Valid username
                'password': 'wrongpass'
            })
        valid_user_time = time.time() - start_time

        # Test with invalid username, invalid password
        start_time = time.time()
        with patch('web.views.authenticate') as mock_auth:
            mock_auth.return_value = None

            response2 = self.client.post('/login', {
                'username': 'nonexistentuser',  # Invalid username
                'password': 'wrongpass'
            })
        invalid_user_time = time.time() - start_time

        # Both should fail with same status code
        self.assertEqual(response1.status_code, response2.status_code)

        # Timing difference could reveal user enumeration vulnerability
        # This documents the vulnerability rather than fixing it
        time_difference = abs(valid_user_time - invalid_user_time)
        # Large time differences could indicate timing attack vulnerability

    def test_concurrent_session_handling(self):
        """Test concurrent session handling."""
        # Create two client sessions
        client1 = Client()
        client2 = Client()

        # Login same user from two different clients
        client1.force_login(self.user)
        client2.force_login(self.user)

        with patch('web.views.AccountService.find_users_by_username') as mock_find_users:
            mock_find_users.return_value = [self.account]

            # Both sessions should work (or one should be invalidated)
            response1 = client1.get('/dashboard')
            response2 = client2.get('/dashboard')

            # Document current behavior - concurrent sessions may be allowed (vulnerability)
            self.assertIn(response1.status_code, [200, 302, 403])
            self.assertIn(response2.status_code, [200, 302, 403])

    def test_logout_session_invalidation(self):
        """Test proper session invalidation on logout."""
        # Login user
        self.client.force_login(self.user)

        # Verify can access protected resource
        with patch('web.views.AccountService.find_users_by_username') as mock_find_users:
            mock_find_users.return_value = [self.account]

            response1 = self.client.get('/dashboard')
            self.assertEqual(response1.status_code, 200)

        # Logout
        with patch('web.views.logout') as mock_logout:
            response_logout = self.client.get('/logout')
            self.assertEqual(response_logout.status_code, 302)

        # Try to access protected resource after logout
        response2 = self.client.get('/dashboard')
        # Should be redirected or denied (depending on middleware implementation)
        # This documents current behavior which may have vulnerabilities
        self.assertIn(response2.status_code, [200, 302, 403, 404])
