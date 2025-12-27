# Services Layer

## Overview

The services layer provides business logic and data access operations. Services are defined in `src/web/services.py` and act as an intermediary between views and models.

## Service Classes

### StorageService

Handles file storage operations for user avatars.

```python
class StorageService:
    folder = os.path.join(settings.BASE_DIR, "web", "static", "resources", "avatars")
```

#### Methods

##### exists(file_name: str) -> bool

Checks if a file exists in the avatars directory.

```python
def exists(self, file_name: str) -> bool:
    file = os.path.join(self.folder, file_name)
    return os.path.exists(file)
```

##### load(file_name: str)

Loads and returns file contents.

```python
def load(self, file_name: str):
    file = os.path.join(self.folder, file_name)
    with open(file, "rb") as fh:
        return fh.read()
```

##### save(data: bytes, file_name: str)

Saves data to a file.

```python
def save(self, data: bytes, file_name: str):
    file = os.path.join(self.folder, file_name)
    with open(file, "wb") as fh:
        fh.write(data)
```

#### Security Issues

- Path traversal vulnerability (no input sanitization)
- Direct file system access
- No file type validation
- No file size limits

### AccountService

Handles user authentication and account management. Implements Django's `BaseBackend` for custom authentication.

```python
class AccountService(BaseBackend):
```

#### Methods

##### authenticate

Authenticates a user and creates/retrieves Django User object.

```python
def authenticate(self, request, username=None, password=None):
    username = request.POST.get("username")
    password = request.POST.get("password")
    accounts = self.find_users_by_username_and_password(username, password)
    if len(accounts) == 0:
        return None
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User(username=username, password=password)
        user.is_staff = True
        user.is_superuser = username == "john"
        user.save()
    return user
```

**Process:**

1. Extract credentials from POST data
2. Query database for matching account (vulnerable to SQL injection)
3. Create or retrieve Django User object
4. Set admin privileges (john is superuser)
5. Return user object

**Security Issues:**

- SQL injection in authentication query
- Superuser status based on username
- No password hashing
- No rate limiting

##### get_user(user_id)

Retrieves a user by ID for Django session management.

```python
def get_user(self, user_id):
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None
```

##### find_users_by_username_and_password

Finds accounts matching username and password.

```python
@staticmethod
def find_users_by_username_and_password(username: str, password: str) -> list[Account]:
    sql = "select * from web_account where username='" + username + "' AND password='" + password + "'"
    return Account.objects.raw(sql)
```

**Security Issues:**

- SQL injection vulnerability (string concatenation)
- Plaintext password comparison
- No prepared statements

##### find_users_by_username

Finds accounts by username.

```python
@staticmethod
def find_users_by_username(username: str) -> list[Account]:
    sql = "select * from web_account where username='" + username + "'"
    return Account.objects.raw(sql)
```

**Security Issues:**

- SQL injection vulnerability

##### find_all_users() -> list[Account]

Returns all user accounts.

```python
@staticmethod
def find_all_users() -> list[Account]:
    sql = "select * from web_account"
    return Account.objects.raw(sql)
```

### CashAccountService

Manages cash account operations.

```python
class CashAccountService:
```

#### Methods

##### find_cash_accounts_by_username

Finds all cash accounts for a user.

```python
@staticmethod
def find_cash_accounts_by_username(username: str) -> list[CashAccount]:
    sql = "select * from web_cashaccount where username='" + username + "'"
    return CashAccount.objects.raw(sql)
```

**Security Issues:**

- SQL injection vulnerability

##### get_from_account_actual_amount

Gets current balance of an account.

```python
@staticmethod
def get_from_account_actual_amount(account: str) -> float:
    sql = "SELECT availableBalance FROM web_cashaccount WHERE number = '" + account + "'"
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchone()
        return row[0]
```

**Security Issues:**

- SQL injection vulnerability
- No error handling for missing accounts

##### get_id_from_number(account: str) -> int

Gets account ID from account number.

```python
@staticmethod
def get_id_from_number(account: str) -> int:
    sql = "SELECT id FROM web_cashaccount WHERE number = '" + account + "'"
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchone()
        return row[0]
```

**Security Issues:**

- SQL injection vulnerability

### CreditAccountService

Manages credit account operations.

```python
class CreditAccountService:
```

#### Methods

##### find_credit_accounts_by_username

Finds all credit accounts for a user.

```python
@staticmethod
def find_credit_accounts_by_username(username: str) -> list[CreditAccount]:
    sql = "select * from web_creditaccount where username='" + username + "'"
    return CreditAccount.objects.raw(sql)
```

**Security Issues:**

- SQL injection vulnerability

##### update_credit_account

Updates credit account balance.

```python
@staticmethod
def update_credit_account(cashAccountId: int, round: float):
    sql = (
        "UPDATE web_creditaccount SET availableBalance='"
        + str(round)
        + "' WHERE cashAccountId ='"
        + str(cashAccountId)
        + "'"
    )
    with connection.cursor() as cursor:
        cursor.execute(sql)
```

**Security Issues:**

- SQL injection vulnerability (even with numeric values)
- No return value or error handling

### ActivityService

Manages transaction history operations.

```python
class ActivityService:
```

#### Methods

##### find_transactions_by_account

Finds all transactions for an account.

```python
@staticmethod
def find_transactions_by_cash_account_number(number: str) -> list[Transaction]:
    sql = "SELECT * FROM web_transaction WHERE number = '" + number + "'"
    return Transaction.objects.raw(sql)
```

**Security Issues:**

- SQL injection vulnerability

##### insert_new_activity

Creates a new transaction record.

```python
@staticmethod
def insert_new_activity(date, description: str, number: str, amount: float, available_balance: float):
    sql = "INSERT INTO web_transaction (date, description, number, amount, availablebalance) VALUES (%s, %s, %s, %s, %s)"
    with connection.cursor() as cursor:
        cursor.execute(sql, [date, description, number, amount, available_balance])
```

**Note:** This method correctly uses parameterized queries.

### TransferService

Manages money transfer operations.

```python
class TransferService:
```

#### Methods

##### insert_transfer(transfer: Transfer)

Inserts a transfer record into the database.

```python
@staticmethod
def insert_transfer(transfer: Transfer):
    sql = (
        "INSERT INTO web_transfer "
        "(fromAccount, toAccount, description, amount, fee, username, date) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )
    with connection.cursor() as cursor:
        cursor.execute(
            sql,
            [
                transfer.fromAccount,
                transfer.toAccount,
                transfer.description,
                transfer.amount,
                transfer.fee,
                transfer.username,
                transfer.date,
            ],
        )
```

**Note:** Uses parameterized queries correctly.

##### createNewTransfer(transfer: Transfer)

Processes a complete money transfer with balance updates.

```python
@staticmethod
@transaction.atomic
def createNewTransfer(transfer: Transfer):
    # Insert transfer record
    TransferService.insert_transfer(transfer)

    # Update from account
    actual_amount = CashAccountService.get_from_account_actual_amount(transfer.fromAccount)
    amount_total = actual_amount - (transfer.amount + transfer.fee)
    amount = actual_amount - transfer.amount
    amount_with_fees = amount - transfer.fee
    cash_account_id = CashAccountService.get_id_from_number(transfer.fromAccount)
    CreditAccountService.update_credit_account(cash_account_id, round(amount_total, 2))

    # Record from account activities
    desc = transfer.description if len(transfer.description) <= 12 else transfer.description[0:12]
    ActivityService.insert_new_activity(
        transfer.date,
        f"TRANSFER: {desc}",
        transfer.fromAccount,
        -round(transfer.amount, 2),
        round(amount, 2),
    )
    ActivityService.insert_new_activity(
        transfer.date,
        "TRANSFER FEE",
        transfer.fromAccount,
        -round(transfer.fee, 2),
        round(amount_with_fees, 2),
    )

    # Update to account
    to_cash_account_id = CashAccountService.get_id_from_number(transfer.toAccount)
    to_actual_amount = CashAccountService.get_from_account_actual_amount(transfer.toAccount)
    to_amount_total = to_actual_amount + transfer.amount
    CreditAccountService.update_credit_account(to_cash_account_id, round(to_amount_total, 2))
    ActivityService.insert_new_activity(
        transfer.date,
        f"TRANSFER: ${desc}",
        transfer.toAccount,
        round(transfer.amount, 2),
        round(to_amount_total, 2),
    )
```

**Process:**

1. Record transfer in transfer table
2. Deduct amount and fee from source account
3. Create transaction records for debit and fee
4. Add amount to destination account
5. Create transaction record for credit

**Transaction Safety:**

Uses `@transaction.atomic` decorator to ensure all operations succeed or fail together.

**Issues:**

- No validation of account ownership
- No balance verification
- No transfer limits
- Truncates description to 12 characters

## Service Design Patterns

### Static Methods

All service methods are static, requiring no instance state:

```python
@staticmethod
def method_name():
    pass
```

**Implications:**

- No shared state between method calls
- Simple to use but less flexible
- Cannot be easily mocked in tests

### Raw SQL Usage

Services primarily use raw SQL instead of Django ORM:

**Pros:**

- Demonstrates SQL injection vulnerabilities
- Direct control over queries
- Educational value

**Cons:**

- Security vulnerabilities
- No query optimization
- No database abstraction
- Maintenance difficulties

### Transaction Management

Transfer operations use Django's transaction management:

```python
from django.db import transaction

@transaction.atomic
def createNewTransfer(transfer: Transfer):
    # Multiple database operations
```

**Benefits:**

- Ensures data consistency
- Automatic rollback on errors
- ACID compliance

## Service Layer Testing

Services are tested in:

- `tests/unit/test_services.py`: Unit tests for service methods
- `tests/integration/`: Integration tests with database

## Service Best Practices (Violated)

The following best practices are intentionally violated:

1. Using raw SQL with string concatenation
2. No input validation or sanitization
3. No error handling
4. No logging
5. Direct database access without abstraction
6. Static methods instead of instance methods
7. No service interfaces or contracts
8. Mixing data access with business logic
9. No transaction isolation levels defined
10. No query optimization or caching

## Related Documentation

- [Models](models.md)
- [Views and URL Routing](views-urls.md)
- [Security Vulnerabilities](security-vulnerabilities.md)
- [Database Schema](database-schema.md)
- [Testing Overview](../testing/overview.md)
