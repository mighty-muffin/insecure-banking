"""Security test specific fixtures and utilities."""

import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def malicious_input_samples():
    """Common malicious input patterns for security testing."""
    return {
        "sql_injection": [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "'; UNION SELECT * FROM users; --"
        ],
        "xss": [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//\"",
        ],
        "command_injection": [
            "; rm -rf /",
            "&& cat /etc/passwd",
            "| nc -l 1234",
            "`whoami`"
        ],
        "path_traversal": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....//....//....//etc/passwd"
        ]
    }


@pytest.fixture
def weak_passwords():
    """Common weak password patterns."""
    return [
        "password",
        "123456",
        "admin",
        "guest",
        "password123",
        "admin123",
        "qwerty",
        "abc123"
    ]


@pytest.fixture
def csrf_attack_client():
    """Client configured for CSRF attack testing."""
    from django.test import Client
    client = Client(enforce_csrf_checks=True)
    return client


@pytest.fixture
def security_headers():
    """Expected security headers for testing."""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'"
    }


@pytest.fixture
def mock_vulnerability_scanner():
    """Mock vulnerability scanner for testing security checks."""
    scanner = Mock()
    scanner.scan_sql_injection = Mock(return_value={"vulnerable": True, "details": "SQL injection detected"})
    scanner.scan_xss = Mock(return_value={"vulnerable": True, "details": "XSS vulnerability found"})
    scanner.scan_csrf = Mock(return_value={"vulnerable": True, "details": "CSRF protection missing"})
    scanner.scan_auth = Mock(return_value={"vulnerable": True, "details": "Weak authentication"})
    return scanner
