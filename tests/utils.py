"""Utility functions and helpers for tests."""

import json
import random
import string
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any


def generate_random_string(length: int = 10) -> str:
    """Generate a random string of specified length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_account_number() -> str:
    """Generate a valid-looking account number."""
    return ''.join(random.choices(string.digits, k=10))


def generate_test_user_data() -> Dict[str, Any]:
    """Generate test user data."""
    username = f"user_{generate_random_string(8)}"
    return {
        "username": username,
        "email": f"{username}@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpass123"
    }


def generate_test_account_data(user_id: int = None) -> Dict[str, Any]:
    """Generate test account data."""
    return {
        "user_id": user_id or 1,
        "account_number": generate_account_number(),
        "balance": Decimal(str(random.uniform(100, 10000))),
        "account_type": random.choice(["checking", "savings"])
    }


def generate_test_transaction_data(account_id: int = None) -> Dict[str, Any]:
    """Generate test transaction data."""
    return {
        "account_id": account_id or 1,
        "amount": Decimal(str(random.uniform(10, 1000))),
        "description": f"Test transaction {generate_random_string(5)}",
        "transaction_type": random.choice(["deposit", "withdrawal", "transfer"])
    }


def create_test_request_data(method: str = "GET", **kwargs) -> Dict[str, Any]:
    """Create test request data."""
    data = {
        "method": method,
        "path": kwargs.get("path", "/test/"),
        "user": kwargs.get("user", None),
        "GET": kwargs.get("GET", {}),
        "POST": kwargs.get("POST", {}),
        "session": kwargs.get("session", {}),
        "META": kwargs.get("META", {})
    }
    return data


def assert_security_headers(response, required_headers: List[str] = None):
    """Assert that security headers are present in response."""
    if required_headers is None:
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection"
        ]

    for header in required_headers:
        assert header in response, f"Missing security header: {header}"


def assert_no_sensitive_data_in_response(response, sensitive_fields: List[str] = None):
    """Assert that sensitive data is not exposed in response."""
    if sensitive_fields is None:
        sensitive_fields = ["password", "secret", "key", "token"]

    content = response.content.decode('utf-8').lower()
    for field in sensitive_fields:
        assert field not in content, f"Sensitive field '{field}' found in response"


def create_mock_vulnerability_report(vulnerability_type: str, severity: str = "high") -> Dict[str, Any]:
    """Create a mock vulnerability report for testing."""
    return {
        "type": vulnerability_type,
        "severity": severity,
        "description": f"Mock {vulnerability_type} vulnerability",
        "location": "test_location",
        "timestamp": datetime.now().isoformat(),
        "details": {
            "input": "test_input",
            "output": "test_output",
            "expected": "safe_output"
        }
    }


def format_coverage_report(coverage_data: Dict[str, Any]) -> str:
    """Format coverage data for readable output."""
    lines = []
    lines.append(f"Total Coverage: {coverage_data.get('total', 0):.1f}%")

    for file_path, file_data in coverage_data.get('files', {}).items():
        coverage = file_data.get('coverage', 0)
        lines.append(f"  {file_path}: {coverage:.1f}%")

    return "\n".join(lines)


class TestDataFactory:
    """Factory class for creating test data."""

    @staticmethod
    def create_user(**overrides):
        """Create test user data with optional overrides."""
        data = generate_test_user_data()
        data.update(overrides)
        return data

    @staticmethod
    def create_account(**overrides):
        """Create test account data with optional overrides."""
        data = generate_test_account_data()
        data.update(overrides)
        return data

    @staticmethod
    def create_transaction(**overrides):
        """Create test transaction data with optional overrides."""
        data = generate_test_transaction_data()
        data.update(overrides)
        return data


class SecurityTestHelpers:
    """Helper methods for security testing."""

    @staticmethod
    def test_sql_injection(client, endpoint: str, parameter: str, payloads: List[str]):
        """Test SQL injection vulnerabilities."""
        results = []
        for payload in payloads:
            data = {parameter: payload}
            response = client.post(endpoint, data)
            results.append({
                "payload": payload,
                "status_code": response.status_code,
                "vulnerable": response.status_code != 400  # Assuming 400 means input validation caught it
            })
        return results

    @staticmethod
    def test_xss_vulnerability(client, endpoint: str, parameter: str, payloads: List[str]):
        """Test XSS vulnerabilities."""
        results = []
        for payload in payloads:
            data = {parameter: payload}
            response = client.post(endpoint, data)
            content = response.content.decode('utf-8')
            results.append({
                "payload": payload,
                "status_code": response.status_code,
                "vulnerable": payload in content  # Payload reflected without escaping
            })
        return results
