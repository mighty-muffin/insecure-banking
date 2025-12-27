# Models

## Overview

The application defines five Django models that represent the core banking domain entities. These models map directly to database tables and provide the data structure for the application.

## Model Definitions

### Account Model

Represents user account information.

```python
class Account(models.Model):
    username = models.CharField(primary_key=True, max_length=80)
    name = models.CharField(max_length=80)
    surname = models.CharField(max_length=80)
    password = models.CharField(max_length=80)
```

#### Fields

- **username**: Primary key, unique identifier for login
- **name**: User's first name
- **surname**: User's last name
- **password**: User's password (stored in plaintext)

#### Methods

No custom methods defined.

#### Security Issues

- Password stored in plaintext (should use Django's password hashing)
- No validation on username format
- No password strength requirements

### CashAccount Model

Represents a cash/checking account.

```python
class CashAccount(models.Model):
    number = models.CharField(max_length=80)
    username = models.CharField(max_length=80)
    description = models.CharField(max_length=80)
    availableBalance = models.FloatField()
```

#### Fields

- **number**: Account number (string format)
- **username**: Owner's username (should be ForeignKey)
- **description**: Account name or description
- **availableBalance**: Current account balance

#### Methods

No custom methods defined.

#### Design Issues

- No foreign key relationship to Account model
- Username stored as string instead of foreign key
- Balance stored as float (precision issues)
- No validation on account numbers

### CreditAccount Model

Represents a credit card or credit line account.

```python
class CreditAccount(models.Model):
    cashAccountId = models.IntegerField()
    number = models.CharField(max_length=80)
    username = models.CharField(max_length=80)
    description = models.CharField(max_length=80)
    availableBalance = models.FloatField()
```

#### Fields

- **cashAccountId**: Associated cash account ID
- **number**: Credit card/account number
- **username**: Owner's username
- **description**: Account description
- **availableBalance**: Available credit balance

#### Methods

No custom methods defined.

#### Design Issues

- No foreign key to CashAccount model
- Username stored as string instead of foreign key
- Balance stored as float
- No credit limit field

### Transfer Model

Represents money transfer transactions.

```python
class Transfer(models.Model, ModelSerializationMixin):
    fromAccount = models.CharField(max_length=80)
    toAccount = models.CharField(max_length=80)
    description = models.CharField(max_length=80)
    amount = models.FloatField()
    fee = models.FloatField(default=20)
    username = models.CharField(max_length=80)
    date = models.DateTimeField()
```

#### Fields

- **fromAccount**: Source account number
- **toAccount**: Destination account number
- **description**: Transfer description
- **amount**: Transfer amount
- **fee**: Transaction fee (default 20)
- **username**: User who initiated the transfer
- **date**: Transfer date and time

#### Methods

Inherits from `ModelSerializationMixin`:

- **as_dict()**: Converts model instance to dictionary
- **from_dict(values)**: Populates model from dictionary

#### Design Issues

- Account references as strings instead of foreign keys
- Username as string instead of foreign key
- Fee default is misleading (actually a percentage)

### Transaction Model

Represents account activity history.

```python
class Transaction(models.Model):
    number = models.CharField(max_length=80)
    description = models.CharField(max_length=80)
    amount = models.FloatField()
    availableBalance = models.FloatField()
    date = models.DateTimeField()
```

#### Fields

- **number**: Account number
- **description**: Transaction description
- **amount**: Transaction amount (positive or negative)
- **availableBalance**: Account balance after transaction
- **date**: Transaction date and time

#### Methods

No custom methods defined.

#### Design Issues

- Account number as string instead of foreign key
- No transaction type field
- No transaction status field

## Model Mixins

### ModelSerializationMixin

A custom mixin that provides serialization capabilities.

```python
class ModelSerializationMixin:
    def as_dict(self) -> dict:
        data = {}
        for field in self._meta.fields:
            value = getattr(self, field.name)
            data[field.name] = value
        return data

    def from_dict(self, values: dict):
        for key, value in values.items():
            setattr(self, key, value)
```

#### Methods

- **as_dict()**: Serializes model instance to dictionary
- **from_dict(values)**: Deserializes dictionary to model instance

#### Usage

Used by the Transfer model for session storage:

```python
# Serialize to session
request.session["pendingTransfer"] = json.dumps(transfer.as_dict())

# Deserialize from session
transfer = Transfer()
transfer.from_dict(json.loads(request.session["pendingTransfer"]))
```

## Model Managers

The models use Django's default manager (`objects`). No custom managers are defined.

## Model Meta Options

No custom Meta classes are defined for any models. All models use Django's default options:

- Table names generated as `app_model` (e.g., `web_account`)
- Default ordering (by primary key)
- No custom permissions
- No indexes defined

## Model Validation

### Field-Level Validation

Models use basic Django field validation:

- **max_length**: Enforced on CharField
- **required**: All fields are required (no blank=True)

### Model-Level Validation

No custom model validation methods (clean, validate_unique, etc.) are implemented.

### Form Validation

The TransferForm provides form-level validation:

```python
class TransferForm(ModelForm):
    class Meta:
        model = Transfer
        fields = ["fromAccount", "toAccount", "description", "amount", "fee"]
```

## Model Relationships

### Intended Relationships

Although not enforced with foreign keys, the intended relationships are:

```text
Account
  └─ has many CashAccount (via username)
       └─ has many CreditAccount (via cashAccountId)
       └─ has many Transaction (via number)

Account
  └─ initiates many Transfer (via username)
```

### Missing Foreign Keys

The application intentionally omits foreign key constraints:

```python
# Should be:
username = models.ForeignKey(Account, on_delete=models.CASCADE)

# Actually is:
username = models.CharField(max_length=80)
```

This design choice:

- Allows for easier SQL injection demonstrations
- Prevents database-level referential integrity
- Enables orphaned records

## Model Queries

### ORM vs Raw SQL

The application primarily uses raw SQL queries instead of Django ORM:

```python
# ORM way (not used):
accounts = Account.objects.filter(username=username, password=password)

# Raw SQL way (used):
sql = "select * from web_account where username='" + username + "' AND password='" + password + "'"
accounts = Account.objects.raw(sql)
```

### Common Query Patterns

```python
# Find user by username
Account.objects.raw("select * from web_account where username='" + username + "'")

# Find cash accounts
CashAccount.objects.raw("select * from web_cashaccount where username='" + username + "'")

# Find transactions
Transaction.objects.raw("SELECT * FROM web_transaction WHERE number = '" + number + "'")
```

## Model Instances

### Creating Instances

```python
# Creating a new transfer
transfer = Transfer()
transfer.fromAccount = "123456"
transfer.toAccount = "789012"
transfer.amount = 100.0
transfer.fee = 5.0
transfer.username = "john"
transfer.date = date.today()
```

### Saving Instances

The application rarely uses model.save(). Instead, it uses raw SQL INSERT statements:

```python
# Not used:
transfer.save()

# Used instead:
TransferService.insert_transfer(transfer)
```

## Model Field Naming

### Naming Convention

The models use mixed naming conventions:

- **camelCase**: availableBalance, fromAccount, toAccount, cashAccountId
- **lowercase**: username, password, name, surname, description, amount, fee

This inconsistency is present throughout the codebase.

## Model Best Practices (Intentionally Violated)

The following Django model best practices are intentionally violated:

1. Using string fields instead of foreign keys
2. Storing passwords in plaintext CharField
3. Using FloatField for currency (should use DecimalField)
4. No model validation methods
5. No custom managers for complex queries
6. No model-level permissions
7. Inconsistent field naming conventions
8. No help_text on fields
9. No verbose_name for fields
10. No model documentation strings

## Model Testing

Models are tested in `tests/unit/test_models.py`:

- Field type validation
- Serialization mixin functionality
- Model creation and retrieval

## Related Documentation

- [Database Schema](database-schema.md)
- [Services Layer](services.md)
- [Views and URL Routing](views-urls.md)
- [Security Vulnerabilities](security-vulnerabilities.md)
