"""Base test classes for different test types."""

import pytest
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from unittest.mock import Mock, patch

from .utils import TestDataFactory, SecurityTestHelpers


class BaseTestCase(TestCase):
    """Base test case with common setup and utilities."""

    def setUp(self):
        """Set up test data."""
        self.factory = TestDataFactory()
        self.user_data = self.factory.create_user()
        self.account_data = self.factory.create_account()
        self.transaction_data = self.factory.create_transaction()

    def create_test_user(self, **overrides):
        """Create a test user in database."""
        data = self.factory.create_user(**overrides)
        return User.objects.create_user(**data)

    def create_test_account(self, user=None, **overrides):
        """Create a test account in database."""
        from web.models import Account

        if user is None:
            user = self.create_test_user()

        data = self.factory.create_account(user_id=user.id, **overrides)
        data['user'] = user  # Replace user_id with user object
        data.pop('user_id', None)

        return Account.objects.create(**data)

    def create_test_transaction(self, account=None, **overrides):
        """Create a test transaction in database."""
        from web.models import Transaction

        if account is None:
            account = self.create_test_account()

        data = self.factory.create_transaction(account_id=account.id, **overrides)
        data['account'] = account  # Replace account_id with account object
        data.pop('account_id', None)

        return Transaction.objects.create(**data)


class BaseUnitTestCase(BaseTestCase):
    """Base class for unit tests with mocking utilities."""

    def setUp(self):
        """Set up unit test environment."""
        super().setUp()
        self.mock_patches = []

    def tearDown(self):
        """Clean up mocks."""
        for patcher in self.mock_patches:
            patcher.stop()

    def mock_model(self, model_path: str, **attributes):
        """Create a mock model with specified attributes."""
        mock_model = Mock()
        for attr, value in attributes.items():
            setattr(mock_model, attr, value)

        patcher = patch(model_path, return_value=mock_model)
        self.mock_patches.append(patcher)
        return patcher.start()

    def mock_service_method(self, service_path: str, method_name: str, return_value=None):
        """Mock a service method."""
        patcher = patch(f"{service_path}.{method_name}", return_value=return_value)
        self.mock_patches.append(patcher)
        return patcher.start()


class BaseIntegrationTestCase(TransactionTestCase):
    """Base class for integration tests."""

    def setUp(self):
        """Set up integration test environment."""
        self.factory = TestDataFactory()
        self.client = self.client_class()
        self.setup_test_data()

    def setup_test_data(self):
        """Set up comprehensive test data for integration tests."""
        # Create multiple users
        self.users = []
        for i in range(3):
            user_data = self.factory.create_user(username=f"testuser{i}")
            user = User.objects.create_user(**user_data)
            self.users.append(user)

        # Create accounts for users
        self.accounts = []
        for user in self.users:
            account = self.create_test_account(user=user)
            self.accounts.append(account)

        # Create transactions
        self.transactions = []
        for account in self.accounts:
            transaction = self.create_test_transaction(account=account)
            self.transactions.append(transaction)

    def create_test_account(self, user=None, **overrides):
        """Create test account for integration testing."""
        from web.models import Account

        if user is None:
            user = self.users[0]

        data = self.factory.create_account(**overrides)
        data['user'] = user

        return Account.objects.create(**data)

    def create_test_transaction(self, account=None, **overrides):
        """Create test transaction for integration testing."""
        from web.models import Transaction

        if account is None:
            account = self.accounts[0]

        data = self.factory.create_transaction(**overrides)
        data['account'] = account

        return Transaction.objects.create(**data)

    def authenticate_user(self, user=None):
        """Authenticate a user for testing."""
        if user is None:
            user = self.users[0]
        self.client.force_login(user)
        return user


class BaseSecurityTestCase(BaseTestCase):
    """Base class for security tests."""

    def setUp(self):
        """Set up security test environment."""
        super().setUp()
        self.security_helpers = SecurityTestHelpers()
        self.csrf_client = self.client_class(enforce_csrf_checks=True)

    def test_sql_injection_protection(self, endpoint: str, parameter: str):
        """Test SQL injection protection for an endpoint."""
        payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "'; UNION SELECT * FROM users; --"
        ]

        results = self.security_helpers.test_sql_injection(
            self.client, endpoint, parameter, payloads
        )

        # Assert that all payloads were properly handled
        for result in results:
            self.assertFalse(
                result['vulnerable'],
                f"SQL injection vulnerability found with payload: {result['payload']}"
            )

    def test_xss_protection(self, endpoint: str, parameter: str):
        """Test XSS protection for an endpoint."""
        payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert(String.fromCharCode(88,83,83))//'"
        ]

        results = self.security_helpers.test_xss_vulnerability(
            self.client, endpoint, parameter, payloads
        )

        # Assert that all payloads were properly escaped
        for result in results:
            self.assertFalse(
                result['vulnerable'],
                f"XSS vulnerability found with payload: {result['payload']}"
            )

    def test_csrf_protection(self, endpoint: str, data: dict = None):
        """Test CSRF protection for an endpoint."""
        if data is None:
            data = {}

        # Test without CSRF token
        response = self.csrf_client.post(endpoint, data)
        self.assertEqual(
            response.status_code, 403,
            "CSRF protection should reject requests without valid token"
        )

    def assert_security_headers(self, response):
        """Assert that required security headers are present."""
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection"
        ]

        for header in required_headers:
            self.assertIn(
                header, response,
                f"Missing required security header: {header}"
            )
