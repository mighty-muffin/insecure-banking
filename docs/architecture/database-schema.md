# Database Schema

## Database Engine

- **Type**: SQLite 3
- **Location**: `src/db.sqlite3`
- **Character Set**: UTF-8
- **Collation**: Default SQLite collation

## Schema Overview

The application uses a simple relational database schema with five main tables representing the banking domain model.

## Tables

### web_account

User account information table.

```sql
CREATE TABLE web_account (
    username VARCHAR(80) PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    surname VARCHAR(80) NOT NULL,
    password VARCHAR(80) NOT NULL
);
```

#### Fields

| Field    | Type         | Constraints | Description                    |
|----------|--------------|-------------|--------------------------------|
| username | VARCHAR(80)  | PRIMARY KEY | Unique username for login      |
| name     | VARCHAR(80)  | NOT NULL    | User's first name              |
| surname  | VARCHAR(80)  | NOT NULL    | User's last name               |
| password | VARCHAR(80)  | NOT NULL    | Password (stored in plaintext) |

#### Security Note

Passwords are stored in plaintext, which is an intentional security vulnerability for educational purposes.

### web_cashaccount

Cash account information table.

```sql
CREATE TABLE web_cashaccount (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number VARCHAR(80) NOT NULL,
    username VARCHAR(80) NOT NULL,
    description VARCHAR(80) NOT NULL,
    availableBalance REAL NOT NULL
);
```

#### Fields

| Field            | Type        | Constraints            | Description                 |
|------------------|-------------|------------------------|-----------------------------|
| id               | INTEGER     | PRIMARY KEY AUTO       | Unique account identifier   |
| number           | VARCHAR(80) | NOT NULL               | Account number              |
| username         | VARCHAR(80) | NOT NULL               | Owner's username            |
| description      | VARCHAR(80) | NOT NULL               | Account description/name    |
| availableBalance | REAL        | NOT NULL               | Current account balance     |

#### Notes

- No foreign key constraint to web_account (intentional)
- Balance stored as REAL (floating-point)

### web_creditaccount

Credit account information table.

```sql
CREATE TABLE web_creditaccount (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cashAccountId INTEGER NOT NULL,
    number VARCHAR(80) NOT NULL,
    username VARCHAR(80) NOT NULL,
    description VARCHAR(80) NOT NULL,
    availableBalance REAL NOT NULL
);
```

#### Fields

| Field            | Type        | Constraints            | Description                    |
|------------------|-------------|------------------------|--------------------------------|
| id               | INTEGER     | PRIMARY KEY AUTO       | Unique account identifier      |
| cashAccountId    | INTEGER     | NOT NULL               | Associated cash account ID     |
| number           | VARCHAR(80) | NOT NULL               | Credit card/account number     |
| username         | VARCHAR(80) | NOT NULL               | Owner's username               |
| description      | VARCHAR(80) | NOT NULL               | Account description            |
| availableBalance | REAL        | NOT NULL               | Available credit/balance       |

#### Notes

- cashAccountId links to web_cashaccount but has no foreign key constraint
- Represents credit cards and credit lines

### web_transfer

Transfer transaction records table.

```sql
CREATE TABLE web_transfer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fromAccount VARCHAR(80) NOT NULL,
    toAccount VARCHAR(80) NOT NULL,
    description VARCHAR(80) NOT NULL,
    amount REAL NOT NULL,
    fee REAL NOT NULL DEFAULT 20,
    username VARCHAR(80) NOT NULL,
    date DATE NOT NULL
);
```

#### Fields

| Field       | Type        | Constraints            | Description                     |
|-------------|-------------|------------------------|---------------------------------|
| id          | INTEGER     | PRIMARY KEY AUTO       | Unique transfer identifier      |
| fromAccount | VARCHAR(80) | NOT NULL               | Source account number           |
| toAccount   | VARCHAR(80) | NOT NULL               | Destination account number      |
| description | VARCHAR(80) | NOT NULL               | Transfer description            |
| amount      | REAL        | NOT NULL               | Transfer amount                 |
| fee         | REAL        | NOT NULL, DEFAULT 20   | Transaction fee                 |
| username    | VARCHAR(80) | NOT NULL               | User who initiated transfer     |
| date        | DATE        | NOT NULL               | Transfer date                   |

#### Notes

- Records all money transfers between accounts
- Fee is calculated as percentage and stored separately

### web_transaction

Transaction history table.

```sql
CREATE TABLE web_transaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number VARCHAR(80) NOT NULL,
    description VARCHAR(80) NOT NULL,
    amount REAL NOT NULL,
    availableBalance REAL NOT NULL,
    date DATETIME NOT NULL
);
```

#### Fields

| Field            | Type        | Constraints            | Description                    |
|------------------|-------------|------------------------|--------------------------------|
| id               | INTEGER     | PRIMARY KEY AUTO       | Unique transaction identifier  |
| number           | VARCHAR(80) | NOT NULL               | Account number                 |
| description      | VARCHAR(80) | NOT NULL               | Transaction description        |
| amount           | REAL        | NOT NULL               | Transaction amount             |
| availableBalance | REAL        | NOT NULL               | Balance after transaction      |
| date             | DATETIME    | NOT NULL               | Transaction date and time      |

#### Notes

- Records all account activity (deposits, withdrawals, transfers, fees)
- Maintains running balance history

## Relationships

### Entity Relationship Diagram

```text
web_account (1) ---- (N) web_cashaccount
                          |
                          | (1:N)
                          |
                     web_creditaccount

web_account (1) ---- (N) web_transfer

web_cashaccount (1) ---- (N) web_transaction
```

### Relationship Details

1. **Account to Cash Account**: One-to-Many
   - One user can have multiple cash accounts
   - No enforced foreign key

2. **Cash Account to Credit Account**: One-to-Many
   - One cash account can have multiple credit accounts linked
   - Relationship through cashAccountId field

3. **Account to Transfer**: One-to-Many
   - One user can initiate multiple transfers
   - No enforced foreign key

4. **Cash Account to Transaction**: One-to-Many
   - One cash account can have multiple transactions
   - Relationship through account number string

## Indexes

The default indexes created by Django and SQLite:

- Primary key indexes on all `id` and `username` fields
- No additional custom indexes defined

## Database Initialization

### Sample Data

The database is initialized with test data including:

- Test user accounts
- Sample cash accounts with balances
- Sample credit accounts
- Historical transactions

### Migration Files

Database schema is managed through Django migrations:

- `web/migrations/0001_initial.py`: Initial schema creation

## Query Patterns

### Vulnerable Query Patterns

The application intentionally uses string concatenation for SQL queries:

```python
# SQL Injection vulnerable
sql = "select * from web_account where username='" + username + "'"
```

```python
# SQL Injection vulnerable
sql = "SELECT * FROM web_transaction WHERE number = '" + number + "'"
```

### Transaction Management

Transfer operations use Django's transaction management:

```python
@transaction.atomic
def createNewTransfer(transfer: Transfer):
    # Multiple database operations in single transaction
    insert_transfer(transfer)
    update_balances()
    insert_activities()
```

## Data Types

### Field Type Mappings

Django Model Field → SQLite Type:

- `CharField` → `VARCHAR(n)`
- `IntegerField` → `INTEGER`
- `FloatField` → `REAL`
- `DateTimeField` → `DATETIME`
- `DateField` → `DATE`

### Precision Issues

Financial amounts are stored as REAL (floating-point), which can lead to precision issues. This is an intentional design flaw for educational purposes.

## Database Access Patterns

### Raw SQL Queries

Most queries use raw SQL through Django's `objects.raw()`:

```python
Account.objects.raw(sql)
CashAccount.objects.raw(sql)
Transaction.objects.raw(sql)
```

### Direct Cursor Access

Some operations use direct database cursor:

```python
with connection.cursor() as cursor:
    cursor.execute(sql)
    row = cursor.fetchone()
```

## Backup and Recovery

### Backup

The SQLite database can be backed up by copying the file:

```bash
cp src/db.sqlite3 src/db.sqlite3.backup
```

### Reset Database

To reset the database:

```bash
rm src/db.sqlite3
python src/manage.py migrate
```

## Performance Considerations

### Limitations

- SQLite is not designed for concurrent writes
- No connection pooling
- Limited to file system I/O performance
- Not suitable for high-traffic applications

### Query Performance

- No query optimization
- No prepared statements
- No query caching
- String concatenation for all queries

## Security Vulnerabilities

### Database-Related Vulnerabilities

1. **SQL Injection**: Raw SQL with string concatenation
2. **No Parameterized Queries**: Direct string formatting
3. **Plaintext Passwords**: No hashing or encryption
4. **Missing Foreign Keys**: No referential integrity
5. **No Input Validation**: Database level constraints missing
6. **Float for Currency**: Precision issues with financial data

## Related Documentation

- [Models](models.md)
- [Services Layer](services.md)
- [Security Vulnerabilities](security-vulnerabilities.md)
- [Application Architecture](overview.md)
