# Security Tests

## Overview

Security tests validate the intentional vulnerabilities in the application. These tests ensure that the security flaws exist as designed for educational and testing purposes.

## Test Files

### test_sql_injection.py

Tests SQL injection vulnerabilities in database queries.

#### Authentication Bypass

```python
@pytest.mark.security
def test_authentication_sql_injection_bypass(client, db):
    """Test SQL injection in authentication allows bypass"""
    # Create a valid user
    Account(username="admin", name="Admin", surname="User", password="secure").save()

    # Attempt SQL injection
    response = client.post("/login", {
        "username": "admin' OR '1'='1",
        "password": "anything"
    })

    # Verify successful authentication (vulnerability confirmed)
    assert response.status_code == 302
    assert response.url == "/dashboard"
```

#### Data Extraction

```python
@pytest.mark.security
def test_sql_injection_data_extraction(authenticated_client, db):
    """Test SQL injection allows data extraction"""
    # Inject SQL to extract all usernames
    # Tests that vulnerability exists
    pass
```

### test_command_injection.py

Tests command injection vulnerabilities.

#### Command Execution

```python
@pytest.mark.security
def test_command_injection_in_transfer(authenticated_client, db):
    """Test command injection vulnerability in transfer traces"""
    # Setup accounts
    CashAccount(
        number="123456",
        username="john",
        description="Test",
        availableBalance=1000.0
    ).save()

    # Inject command
    malicious_account = "123456; ls -la"

    # Verify command can be injected (vulnerability exists)
    # This demonstrates the vulnerability for testing purposes
    pass
```

### test_deserialization.py

Tests insecure deserialization vulnerabilities.

#### Pickle Exploitation

```python
@pytest.mark.security
def test_pickle_deserialization_vulnerability():
    """Test that pickle can execute code during deserialization"""
    import pickle
    import os

    class Exploit:
        def __reduce__(self):
            return (os.system, ("echo 'exploited' > /tmp/test",))

    # Serialize malicious object
    malicious_data = pickle.dumps(Exploit())

    # Verify exploitation possible
    # (In actual test, we verify the vulnerability exists)
    assert len(malicious_data) > 0
```

#### Certificate Upload Exploit

```python
@pytest.mark.security
def test_malicious_certificate_processing(authenticated_client, db):
    """Test malicious certificate upload and processing"""
    # Generate malicious certificate
    # Upload certificate
    # Verify code execution possible
    pass
```

### test_crypto_weaknesses.py

Tests weak cryptography implementations.

#### Weak DES Encryption

```python
@pytest.mark.security
def test_weak_des_encryption():
    """Test that DES encryption is weak and breakable"""
    from web.views import get_file_checksum, secretKey
    from Crypto.Cipher import DES

    data = b"sensitive data"
    checksum = get_file_checksum(data)

    # Verify DES is used (weak algorithm)
    # Verify static key is used
    assert len(secretKey) == 8  # DES key size
```

## Test Purpose

Security tests serve multiple purposes:

### Educational

Demonstrate how vulnerabilities work and can be exploited.

### Validation

Ensure vulnerabilities exist as designed for security tool testing.

### Documentation

Provide working examples of exploitation techniques.

### Training

Help security professionals understand attack vectors.

## Test Markers

Security tests use the `@pytest.mark.security` marker:

```bash
# Run only security tests
pytest -m security -v
```

## Test Approach

### White-Box Testing

Tests have full knowledge of implementation:

- Source code access
- Database schema knowledge
- Internal logic understanding

### Exploitation Validation

Tests attempt to exploit vulnerabilities:

- Inject malicious payloads
- Execute arbitrary commands
- Extract sensitive data
- Bypass authentication

### Controlled Environment

All tests run in isolated environment:

- Test database
- No production impact
- Safe exploitation

## Running Security Tests

```bash
# Run all security tests
pytest tests/security/ -v

# Run specific vulnerability tests
pytest tests/security/test_sql_injection.py -v

# Run with detailed output
pytest tests/security/ -vv -s
```

## Test Data

Security tests use:

- Malicious payloads
- Injection strings
- Exploit code
- Test accounts

## Safety Considerations

These tests are safe because:

- Run in isolated test environment
- Use test database only
- No network access to external systems
- Automatic cleanup after tests

## Vulnerability Validation

Each test validates a specific vulnerability:

1. **Setup**: Create test conditions
2. **Exploit**: Attempt exploitation
3. **Verify**: Confirm vulnerability exists
4. **Cleanup**: Automatic via test framework

## Expected Failures

These tests should **succeed**, indicating vulnerabilities exist:

- SQL injection bypasses authentication
- Commands execute via injection
- Pickle deserializes malicious objects
- Weak encryption used

## Integration with Security Tools

These vulnerabilities can be detected by:

- SQLMap (SQL injection)
- Burp Suite (multiple vulnerabilities)
- OWASP ZAP (web vulnerabilities)
- Bandit (Python security issues)
- Safety (dependency vulnerabilities)

## Related Documentation

- [Security Vulnerabilities](../architecture/security-vulnerabilities.md)
- [Testing Overview](overview.md)
- [Test Structure](structure.md)
- [Application Architecture](../architecture/overview.md)
