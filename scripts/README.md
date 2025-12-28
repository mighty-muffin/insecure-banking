# Fake Banking Data Generator

This directory contains a script to generate realistic fake banking data for the insecure-banking application.

## Script: `generate_fake_data.py`

Generates believable banking records including user accounts, cash accounts, credit cards, and transaction history in SQL INSERT statement format.

### Features

- **User Accounts**: Generates random usernames, first names, last names
- **Cash Accounts**: Creates checking, savings, and IRA accounts with realistic balances
- **Credit Cards**: Generates credit cards linked to checking accounts (Visa, MasterCard, AmEx)
- **Transactions**: Creates transaction history with various merchant types and dates
- **Reproducible**: Supports seeding for consistent output

### Usage

```bash
# Basic usage - generates 7 accounts and prints to stdout
python scripts/generate_fake_data.py

# Generate specific number of accounts
python scripts/generate_fake_data.py -n 10

# Generate reproducible data with seed
python scripts/generate_fake_data.py -s 42

# Save output to file
python scripts/generate_fake_data.py -o output.sql

# Combined options
python scripts/generate_fake_data.py -n 15 -s 123 -o scripts/fake_data.sql
```

### Command Line Options

- `-n, --num-accounts`: Number of user accounts to generate (default: 7)
- `-s, --seed`: Random seed for reproducible output (optional)
- `-o, --output`: Output file path (default: print to stdout)
- `-h, --help`: Show help message

### Examples

**Generate data for testing:**

```bash
python scripts/generate_fake_data.py -n 20 -o test_data.sql
```

**Generate consistent data for development:**

```bash
python scripts/generate_fake_data.py -n 20 -s 42 -o fake_data.sql
```

**Quick preview:**

```bash
python scripts/generate_fake_data.py -n 3 | head -50
```

### Output Format

The script generates SQL INSERT statements compatible with the Django models:

```sql
INSERT INTO web_account (username, name, surname, password) VALUES (...);
INSERT INTO web_cashaccount (id, number, username, availableBalance, description) VALUES (...);
INSERT INTO web_creditaccount (id, number, username, description, availableBalance, cashAccountId) VALUES (...);
INSERT INTO web_transaction ("date", description, number, amount, availableBalance) VALUES (...);
```

### Data Structure

- Each user gets 1-4 cash accounts (checking, savings, or IRA)
- ~50% of checking accounts receive a credit card
- Each cash account gets 5-15 transactions
- Transaction dates span 6 months to 5 years depending on account type
- All accounts use password `'test'` for easy testing

### Dependencies

- Python 3.10+
- Faker library (automatically installed via `uv sync`)

### Installation

Ensure dependencies are installed:

```bash
uv sync
```

### Notes

- Account numbers are 20 digits
- Credit card numbers are in format `XXXX XXXX XXXX XXXX`
- Balances are calculated chronologically for consistency
- Transaction types include salary, retirement, purchases, and services
- Retirement accounts have longer transaction histories
