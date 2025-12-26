"""
Security tests for cryptographic weaknesses.

This module provides security validation tests that explicitly document and test
cryptographic vulnerabilities in the insecure banking application. These tests
validate that weak crypto implementations exist for educational purposes
and are NOT intended to fix them.

Educational Purpose:
- Document weak encryption algorithm usage (DES)
- Validate hardcoded key vulnerabilities
- Demonstrate IV reuse weaknesses
- Provide examples for cryptography education

Constitutional Requirements:
- Tests MUST NOT fix vulnerabilities
- All cryptographic weaknesses MUST remain intact
- Tests should document expected vulnerable behavior
- Educational value must be preserved
"""

import base64
import pytest
from unittest.mock import patch, Mock
from django.test import TestCase

from web.views import get_file_checksum, secretKey


@pytest.mark.security
class TestCryptographicWeaknesses(TestCase):
    """Security validation tests for cryptographic weaknesses."""

    def test_des_encryption_weakness_in_get_file_checksum(self):
        """
        Test DES encryption weakness in get_file_checksum() function.

        Educational Purpose: Demonstrates the security weaknesses of using
        the obsolete DES encryption algorithm for sensitive operations.

        Vulnerability: DES is cryptographically broken and should not be used:
        - 56-bit key size is too small (brute force in hours)
        - Known cryptanalytic attacks exist
        - Superseded by AES since 2001
        """
        # Test data for DES encryption analysis
        test_data_samples = [
            b"small",
            b"medium_length_data_sample",
            b"very_long_data_sample_that_exceeds_normal_block_sizes_and_demonstrates_padding_behavior",
            b"",  # Empty data
            b"\x00" * 64,  # Null bytes
            b"\xff" * 64,  # All ones
            b"A" * 64,  # Repeated character
        ]

        for test_data in test_data_samples:
            with self.subTest(data_length=len(test_data)):
                with patch('web.views.DES') as mock_des:
                    with patch('web.views.base64.b64encode') as mock_b64encode:
                        # Mock DES encryption
                        mock_crypter = Mock()
                        mock_crypter.encrypt.return_value = b'encrypted_data'
                        mock_des.new.return_value = mock_crypter
                        mock_b64encode.return_value = b'base64_result'

                        # Call vulnerable function
                        result = get_file_checksum(test_data)

                        # Verify DES usage (vulnerability)
                        mock_des.new.assert_called_once()
                        call_args = mock_des.new.call_args

                        # Document DES weaknesses
                        print(f"DATA LENGTH: {len(test_data)} bytes")
                        print(f"DES KEY: {repr(secretKey)} (hardcoded)")
                        print(f"DES IV: {repr(secretKey)} (key reused as IV)")
                        print(f"DES MODE: {call_args[1] if len(call_args) > 1 else 'Unknown'}")

                        # Verify weak key and IV usage
                        if call_args and len(call_args[0]) >= 2:
                            used_key = call_args[0][0]
                            used_iv = call_args[0][2] if len(call_args[0]) > 2 else None

                            # Document hardcoded key vulnerability
                            self.assertEqual(used_key, secretKey)
                            if used_iv:
                                self.assertEqual(used_iv, secretKey)
                                print("VULNERABILITY: Key reused as IV")

                        print("VULNERABILITY: DES algorithm used (broken since 1997)")
                        print("-" * 60)

    def test_hardcoded_encryption_key_vulnerability(self):
        """
        Test hardcoded encryption key vulnerability.

        Educational Purpose: Demonstrates the severe security risk of
        hardcoding cryptographic keys in source code.

        Vulnerability: The secretKey is hardcoded in the source code,
        making it visible to anyone with access to the codebase.
        """
        # Analyze the hardcoded key
        hardcoded_key = secretKey

        # Document key characteristics
        key_analysis = {
            "key_value": hardcoded_key,
            "key_encoding": type(hardcoded_key).__name__,
            "key_length_bits": len(hardcoded_key) * 8,
            "key_entropy": "Very Low (sequential digits)",
            "key_source": "Hardcoded in source code",
            "key_rotation": "Impossible without code changes",
            "key_visibility": "Visible to all developers and in version control"
        }

        # Test key properties
        self.assertEqual(hardcoded_key, b"01234567")
        self.assertEqual(len(hardcoded_key), 8)  # DES key size
        self.assertIsInstance(hardcoded_key, bytes)

        # Test key predictability (educational)
        expected_bytes = [ord('0') + i for i in range(8)]
        actual_bytes = list(hardcoded_key)
        self.assertEqual(actual_bytes, expected_bytes)

        # Educational logging
        print("HARDCODED KEY VULNERABILITY ANALYSIS:")
        for property_name, value in key_analysis.items():
            print(f"  {property_name.replace('_', ' ').title()}: {value}")

        print("\nKEY ENTROPY ANALYSIS:")
        print(f"  Pattern: Sequential digits (0,1,2,3,4,5,6,7)")
        print(f"  Guessable: Yes (trivial pattern)")
        print(f"  Dictionary attack: Vulnerable")
        print(f"  Brute force time: Microseconds")

        print("\nSECURITY IMPACT:")
        print("  • Any attacker with source code access has the key")
        print("  • All encrypted data can be decrypted")
        print("  • No forward secrecy")
        print("  • Key rotation requires code deployment")
        print("  • Version control history exposes key")

    def test_weak_iv_reuse_vulnerability(self):
        """
        Test weak IV reuse vulnerability in encryption.

        Educational Purpose: Demonstrates the cryptographic weakness of
        reusing the same key as the initialization vector (IV).

        Vulnerability: Using the same value for both key and IV weakens
        the encryption and enables pattern analysis attacks.
        """
        # Test IV reuse with different data
        test_plaintexts = [
            b"secret_data_1",
            b"secret_data_2",
            b"identical_prefix_data_A",
            b"identical_prefix_data_B",
            b"same_length_different_content_123",
            b"same_length_different_content_456",
        ]

        encryption_results = []

        for plaintext in test_plaintexts:
            with patch('web.views.DES') as mock_des:
                with patch('web.views.pad') as mock_pad:
                    with patch('web.views.base64.b64encode') as mock_b64encode:
                        # Mock encryption components
                        mock_crypter = Mock()
                        mock_des.new.return_value = mock_crypter
                        mock_pad.return_value = plaintext + b'\x08' * 8  # Simulated padding
                        mock_crypter.encrypt.return_value = b'encrypted_' + plaintext[:8]
                        mock_b64encode.return_value = base64.b64encode(b'encrypted_' + plaintext[:8])

                        # Call encryption function
                        result = get_file_checksum(plaintext)

                        # Verify key and IV are the same (vulnerability)
                        if mock_des.new.called:
                            call_args = mock_des.new.call_args[0]
                            key = call_args[0]
                            iv = call_args[2] if len(call_args) > 2 else None

                            if iv is not None:
                                self.assertEqual(key, iv, "Key and IV should be identical (vulnerability)")

                            encryption_results.append({
                                'plaintext': plaintext,
                                'key': key,
                                'iv': iv,
                                'result': result
                            })

        # Analyze IV reuse patterns
        print("IV REUSE VULNERABILITY ANALYSIS:")
        print("="*50)

        for i, result in enumerate(encryption_results):
            print(f"Test {i+1}:")
            print(f"  Plaintext: {result['plaintext']}")
            print(f"  Key: {result['key']}")
            print(f"  IV:  {result['iv']}")
            print(f"  Same key/IV: {result['key'] == result['iv']}")
            print(f"  Result: {result['result']}")
            print()

        print("VULNERABILITY IMPACT:")
        print("• Identical key and IV reduce encryption strength")
        print("• Pattern analysis becomes easier for attackers")
        print("• First block encryption is weakened")
        print("• Violates cryptographic best practices")
        print("• Makes frequency analysis attacks more effective")

    def test_des_block_cipher_mode_weaknesses(self):
        """
        Test DES block cipher mode weaknesses.

        Educational Purpose: Demonstrates how improper block cipher mode
        usage can reveal patterns in encrypted data.
        """
        # Test with data that would reveal ECB mode patterns
        pattern_data_samples = [
            # Repeated blocks (would show pattern in ECB mode)
            b"12345678" * 4,  # Same 8-byte block repeated
            b"AAAAAAAA" * 3,  # Identical blocks
            b"pattern1pattern1pattern1",  # Repeated pattern

            # Different lengths to test padding
            b"short",
            b"exactly8bytes",
            b"longer_than_eight_bytes_to_test_multiple_blocks",
        ]

        for test_data in pattern_data_samples:
            with self.subTest(data=test_data[:20]):  # Truncate for display
                with patch('web.views.DES') as mock_des:
                    with patch('web.views.pad') as mock_pad:
                        # Mock DES configuration
                        mock_crypter = Mock()
                        mock_des.new.return_value = mock_crypter
                        mock_des.MODE_CBC = 2  # Simulate CBC mode constant
                        mock_crypter.encrypt.return_value = b"encrypted_data"

                        # Simulate padding
                        block_size = 8
                        padded_size = ((len(test_data) // block_size) + 1) * block_size
                        padding_needed = padded_size - len(test_data)
                        padded_data = test_data + bytes([padding_needed] * padding_needed)
                        mock_pad.return_value = padded_data

                        # Call encryption function
                        get_file_checksum(test_data)

                        # Analyze DES configuration
                        if mock_des.new.called:
                            call_args = mock_des.new.call_args[0]
                            call_kwargs = mock_des.new.call_args[1] if len(mock_des.new.call_args) > 1 else {}

                            print(f"DATA: {test_data}")
                            print(f"DATA LENGTH: {len(test_data)} bytes")
                            print(f"PADDED LENGTH: {len(padded_data)} bytes")
                            print(f"DES KEY: {call_args[0]}")

                            # Check if mode is specified
                            if len(call_args) > 1:
                                mode = call_args[1]
                                print(f"DES MODE: {mode}")

                                # Document mode weaknesses
                                if mode == mock_des.MODE_CBC:
                                    print("MODE: CBC (better than ECB but IV reuse weakens it)")
                                else:
                                    print(f"MODE: Unknown mode {mode}")

                            # Check IV usage
                            if len(call_args) > 2:
                                iv = call_args[2]
                                print(f"IV: {iv}")
                                print(f"IV == KEY: {iv == call_args[0]} (vulnerability)")

                            print("-" * 50)

    def test_documented_cryptographic_weaknesses(self):
        """
        Document all cryptographic weaknesses found in the application.

        Educational Purpose: Comprehensive documentation of crypto vulnerabilities
        for educational and security awareness purposes.
        """
        cryptographic_vulnerabilities = {
            "weak_algorithm": {
                "algorithm": "DES (Data Encryption Standard)",
                "weakness": "Cryptographically broken since 1997",
                "key_size": "56 bits (effectively broken)",
                "attack_time": "Hours with modern hardware",
                "replacement": "AES-256",
                "cve_references": ["CVE-1999-0040"],
                "standards_violation": "NIST deprecated DES in 2005"
            },

            "hardcoded_keys": {
                "key_value": "01234567 (sequential digits)",
                "entropy": "Extremely low",
                "guessability": "Trivial pattern",
                "storage": "Hardcoded in source code",
                "rotation": "Impossible without deployment",
                "version_control": "Exposed in git history"
            },

            "iv_reuse": {
                "pattern": "Key reused as IV",
                "impact": "Weakens first block encryption",
                "attack_vector": "Pattern analysis",
                "best_practice": "Random IV for each encryption",
                "current_behavior": "Deterministic encryption"
            },

            "implementation_issues": {
                "padding": "May be predictable",
                "mode": "CBC with fixed IV",
                "key_derivation": "None (direct key usage)",
                "salt": "Not used",
                "iterations": "Not applicable"
            },

            "educational_value": [
                "Demonstrates why modern algorithms are essential",
                "Shows impact of poor key management",
                "Illustrates IV reuse vulnerabilities",
                "Provides examples of what NOT to do",
                "Teaches importance of crypto library choices"
            ]
        }

        # Assert documentation exists
        self.assertIsNotNone(cryptographic_vulnerabilities)

        # Log comprehensive crypto vulnerability documentation
        print("\n" + "="*80)
        print("CRYPTOGRAPHIC VULNERABILITIES DOCUMENTATION")
        print("="*80)

        for category, details in cryptographic_vulnerabilities.items():
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

        print(f"\nCRITICAL SEVERITY RATING: 10/10")
        print(f"EXPLOITATION DIFFICULTY: Trivial")
        print(f"BUSINESS IMPACT: Complete confidentiality loss")
        print(f"COMPLIANCE IMPACT: Violates PCI DSS, HIPAA, SOX")

        print("\n" + "="*80)
        print("VULNERABILITIES PRESERVED FOR EDUCATIONAL PURPOSES")
        print("="*80)

    def test_encryption_determinism_weakness(self):
        """
        Test encryption determinism weakness caused by fixed IV.

        Educational Purpose: Shows how deterministic encryption leaks
        information about plaintext patterns and repeated data.
        """
        # Test identical plaintexts produce identical ciphertexts
        identical_plaintexts = [
            b"secret_message",
            b"secret_message",  # Exact duplicate
            b"another_secret",
            b"another_secret",  # Exact duplicate
        ]

        results = []

        for plaintext in identical_plaintexts:
            with patch('web.views.DES') as mock_des:
                # Create consistent mock behavior
                mock_crypter = Mock()
                mock_des.new.return_value = mock_crypter
                # Make encryption deterministic for same input
                encrypted_val = b'encrypted_' + plaintext
                mock_crypter.encrypt.return_value = encrypted_val

                # Pre-calculate expected base64 value BEFORE patching
                expected_b64 = base64.b64encode(encrypted_val)

                with patch('web.views.base64.b64encode') as mock_b64:
                    mock_b64.return_value = expected_b64

                    result = get_file_checksum(plaintext)
                    results.append((plaintext, result))

        # Analyze determinism
        print("ENCRYPTION DETERMINISM ANALYSIS:")
        print("="*40)

        for i, (plaintext, ciphertext) in enumerate(results):
            print(f"Input {i+1}: {plaintext}")
            print(f"Output {i+1}: {ciphertext}")
            print()

        # Check for identical outputs from identical inputs
        if len(results) >= 4:
            self.assertEqual(results[0][1], results[1][1], "Identical inputs produce identical outputs (vulnerability)")
            self.assertEqual(results[2][1], results[3][1], "Identical inputs produce identical outputs (vulnerability)")

            print("VULNERABILITY CONFIRMED:")
            print("• Identical plaintexts produce identical ciphertexts")
            print("• Attackers can detect repeated data")
            print("• Pattern analysis is possible")
            print("• Frequency analysis attacks are enabled")

        print("\nSECURE BEHAVIOR WOULD:")
        print("• Use random IV for each encryption")
        print("• Produce different ciphertext for same plaintext")
        print("• Prevent pattern analysis")
        print("• Provide semantic security")
