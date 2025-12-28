"""
Generate realistic fake banking data for the insecure banking application.

This script uses the Faker library to create believable banking records
including accounts, cash accounts, credit accounts, and transactions
in SQL INSERT statement format matching the data.sql schema.
"""

import argparse
import random
from datetime import datetime, timedelta
from typing import List, Tuple

from faker import Faker

# Common weak passwords often found in password lists
COMMON_WEAK_PASSWORDS = [
    'password', 'password123', '123456', '12345678', 'qwerty',
    'abc123', 'monkey', 'letmein', 'dragon', 'master',
    'sunshine', 'princess', 'welcome', 'shadow', 'football',
    'iloveyou', 'admin', 'password1', '123456789', 'baseball',
    'trustno1', 'superman', 'hello', 'freedom', 'whatever',
    'ninja', 'mustang', 'starwars', 'cheese', 'summer',
]


def generate_accounts(fake: Faker, num_accounts: int = 7) -> List[Tuple]:
    """
    Generate fake user accounts with username, name, surname, and password.
    Uses Quebec French localization for authentic French Canadian names.
    Always includes 'Guillaume Bourbonnais' as the first account with
    password 'timinou'. Other accounts get common weak passwords.

    Parameters:
        fake (Faker): Faker instance for generating fake data.
        num_accounts (int): Number of accounts to generate.

    Returns:
        List[Tuple]: List of tuples containing account data
                     (username, name, surname, password).
    """
    accounts = []
    used_usernames = set()

    # Always add Guillaume Bourbonnais as the first account with 'timinou'
    accounts.append(('guillaume', 'Guillaume', 'Bourbonnais', 'timinou'))
    used_usernames.add('guillaume')

    # Generate remaining accounts randomly
    for _ in range(num_accounts - 1):
        # Generate unique username from first name
        while True:
            first_name = fake.first_name()
            username = first_name.lower()
            if username not in used_usernames:
                used_usernames.add(username)
                break

        surname = fake.last_name()
        # Use a common weak password from the list
        password = random.choice(COMMON_WEAK_PASSWORDS)
        accounts.append((username, first_name, surname, password))

    return accounts


def generate_account_number(length: int = 20) -> str:
    """
    Generate a random account number of specified length.

    Parameters:
        length (int): Length of the account number.

    Returns:
        str: Random account number as string.
    """
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def generate_credit_card_number() -> str:
    """
    Generate a fake credit card number in format XXXX XXXX XXXX XXXX.

    Returns:
        str: Formatted credit card number.
    """
    parts = [
        str(random.randint(4000, 5999)),  # Start with 4 or 5 (Visa/MC)
        str(random.randint(1000, 9999)),
        str(random.randint(1000, 9999)),
        str(random.randint(1000, 9999))
    ]
    return ' '.join(parts)


def generate_cash_accounts(
    accounts: List[Tuple],
    min_accounts_per_user: int = 1,
    max_accounts_per_user: int = 4
) -> List[Tuple]:
    """
    Generate cash accounts for users with random balances and descriptions.

    Parameters:
        accounts (List[Tuple]): List of user accounts.
        min_accounts_per_user (int): Minimum cash accounts per user.
        max_accounts_per_user (int): Maximum cash accounts per user.

    Returns:
        List[Tuple]: List of tuples containing cash account data
                     (id, number, username, balance, description).
    """
    cash_accounts = []
    account_id = 1
    account_types = [
        'Checking Account',
        'Savings account',
        'Individual Retirement Accounts (IRAs)'
    ]

    for username, _, _, _ in accounts:
        num_accounts = random.randint(
            min_accounts_per_user,
            max_accounts_per_user
        )
        for _ in range(num_accounts):
            number = generate_account_number(20)
            # Generate realistic balance between $10 and $100,000
            balance = round(random.uniform(10.0, 100000.0), 2)
            description = random.choice(account_types)
            cash_accounts.append(
                (account_id, number, username, balance, description)
            )
            account_id += 1

    return cash_accounts


def generate_credit_accounts(
    cash_accounts: List[Tuple],
    coverage_ratio: float = 0.5
) -> List[Tuple]:
    """
    Generate credit accounts linked to cash accounts.

    Parameters:
        cash_accounts (List[Tuple]): List of cash accounts.
        coverage_ratio (float): Ratio of cash accounts that get credit cards.

    Returns:
        List[Tuple]: List of tuples containing credit account data
                     (id, number, username, description, balance,
                      cash_account_id).
    """
    credit_accounts = []
    credit_card_types = [
        'Visa Gold',
        'Visa Electron',
        'MasterCard',
        'AmEx Gold'
    ]
    account_id = 1

    # Filter to only checking accounts for credit cards
    checking_accounts = [
        acc for acc in cash_accounts
        if 'Checking' in acc[4]
    ]

    # Select random subset of checking accounts for credit cards
    num_credit_accounts = int(len(checking_accounts) * coverage_ratio)
    selected_accounts = random.sample(
        checking_accounts,
        min(num_credit_accounts, len(checking_accounts))
    )

    for cash_id, _, username, balance, _ in selected_accounts:
        card_number = generate_credit_card_number()
        card_type = random.choice(credit_card_types)
        credit_accounts.append(
            (account_id, card_number, username, card_type, balance, cash_id)
        )
        account_id += 1

    return credit_accounts


def generate_transactions(
    fake: Faker,
    cash_accounts: List[Tuple],
    min_transactions: int = 5,
    max_transactions: int = 15
) -> List[Tuple]:
    """
    Generate transaction history for cash accounts.

    Parameters:
        fake (Faker): Faker instance for generating fake data.
        cash_accounts (List[Tuple]): List of cash accounts.
        min_transactions (int): Minimum transactions per account.
        max_transactions (int): Maximum transactions per account.

    Returns:
        List[Tuple]: List of tuples containing transaction data
                     (date, description, account_number, amount, balance).
    """
    transactions = []
    transaction_types = {
        'debit': [
            'Pet Store', 'Grocery Store', 'Sports Store', 'Wood Supply',
            'Pizza Delivery', 'WebHosting', 'Computer Store',
            'Mobile Phone Store', 'Restaurant New York',
            'Restaurant Madrid', 'Gas Station', 'Coffee Shop',
            'Online Shopping', 'Pharmacy', 'Movie Theater'
        ],
        'credit': [
            'Salary', 'Retirement', 'Refund', 'Interest Payment',
            'Bonus', 'Freelance Income'
        ]
    }

    for _, account_number, _, final_balance, description in cash_accounts:
        num_transactions = random.randint(min_transactions, max_transactions)

        # Start with an initial balance and work backwards
        current_balance = final_balance
        account_transactions = []

        # Generate dates going backwards from recent to oldest
        end_date = datetime.now()
        # Retirement accounts have older transactions
        if 'Retirement' in description:
            start_date = end_date - timedelta(days=random.randint(1095, 1825))
        else:
            start_date = end_date - timedelta(days=random.randint(180, 730))

        for i in range(num_transactions):
            # Determine if this is a credit or debit transaction
            # More debits than credits for realistic banking
            is_credit = random.random() < 0.2

            if is_credit:
                trans_description = random.choice(transaction_types['credit'])
                # Credits are larger for salary/retirement
                if 'Retirement' in trans_description:
                    amount = round(random.uniform(1000, 15000), 2)
                else:
                    amount = round(random.uniform(500, 5000), 2)
            else:
                trans_description = random.choice(transaction_types['debit'])
                amount = -round(random.uniform(10, 2000), 2)

            # Calculate previous balance
            previous_balance = round(current_balance - amount, 2)

            # Generate random date within range
            days_range = (end_date - start_date).days
            random_days = random.randint(0, days_range)
            trans_date = start_date + timedelta(days=random_days)
            date_str = trans_date.strftime('%Y-%m-%d %H:%M:%S.%f')

            account_transactions.append(
                (date_str, trans_description, account_number, amount,
                 current_balance)
            )

            current_balance = previous_balance

        # Sort transactions by date (oldest first)
        account_transactions.sort(key=lambda x: x[0])

        # Recalculate balances chronologically for consistency
        running_balance = current_balance
        for trans in account_transactions:
            running_balance = round(running_balance + trans[3], 2)
            transactions.append(
                (trans[0], trans[1], trans[2], trans[3], running_balance)
            )

    return transactions


def format_sql_insert(
    table_name: str,
    columns: List[str],
    values: List[Tuple]
) -> str:
    """
    Format data as SQL INSERT statements.

    Parameters:
        table_name (str): Name of the database table.
        columns (List[str]): List of column names.
        values (List[Tuple]): List of value tuples to insert.

    Returns:
        str: Formatted SQL INSERT statements.
    """
    sql_statements = []
    column_str = ', '.join(columns)

    for value_tuple in values:
        # Format values, handling strings with quotes
        formatted_values = []
        for val in value_tuple:
            if isinstance(val, str):
                # Escape single quotes in strings
                escaped_val = val.replace("'", "''")
                formatted_values.append(f"'{escaped_val}'")
            elif isinstance(val, (int, float)):
                # Numbers with explicit sign for amounts
                if isinstance(val, float) and val > 0 and 'amount' in str(
                    columns
                ).lower():
                    formatted_values.append(f'+{val}')
                else:
                    formatted_values.append(str(val))
            else:
                formatted_values.append(str(val))

        values_str = ', '.join(formatted_values)
        sql_statements.append(
            f"INSERT INTO {table_name} ({column_str}) "
            f"VALUES ({values_str});"
        )

    return '\n'.join(sql_statements)


def generate_banking_data(
    num_accounts: int = 7,
    seed: int = None,
    output_file: str = None
) -> str:
    """
    Generate complete banking dataset with accounts, cash accounts,
    credit accounts, and transactions.

    Parameters:
        num_accounts (int): Number of user accounts to generate.
        seed (int): Random seed for reproducibility.
        output_file (str): Optional file path to write SQL output.

    Returns:
        str: Complete SQL INSERT statements for all tables.
    """
    if seed is not None:
        random.seed(seed)
        Faker.seed(seed)

    # Use Quebec French localization for authentic French Canadian names
    fake = Faker('fr_CA')
    sql_output = []

    # Generate accounts
    accounts = generate_accounts(fake, num_accounts)
    sql_output.append(
        format_sql_insert(
            'web_account',
            ['username', 'name', 'surname', 'password'],
            accounts
        )
    )
    sql_output.append('')  # Blank line for readability

    # Generate cash accounts
    cash_accounts = generate_cash_accounts(accounts)
    sql_output.append(
        format_sql_insert(
            'web_cashaccount',
            ['id', 'number', 'username', 'availableBalance', 'description'],
            cash_accounts
        )
    )
    sql_output.append('')

    # Generate credit accounts
    credit_accounts = generate_credit_accounts(cash_accounts)
    sql_output.append(
        format_sql_insert(
            'web_creditaccount',
            ['id', 'number', 'username', 'description',
             'availableBalance', 'cashAccountId'],
            credit_accounts
        )
    )
    sql_output.append('')

    # Generate transactions
    transactions = generate_transactions(fake, cash_accounts)
    sql_output.append(
        format_sql_insert(
            'web_transaction',
            ['"date"', 'description', 'number',
             'amount', 'availableBalance'],
            transactions
        )
    )

    complete_sql = '\n'.join(sql_output)

    # Write to file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(complete_sql)
        print(f"Generated SQL data written to: {output_file}")

    return complete_sql


def main():
    """
    Main entry point for the script with command-line argument parsing.
    """
    parser = argparse.ArgumentParser(
        description='Generate fake banking data for insecure-banking app'
    )
    parser.add_argument(
        '-n', '--num-accounts',
        type=int,
        default=7,
        help='Number of user accounts to generate (default: 7)'
    )
    parser.add_argument(
        '-s', '--seed',
        type=int,
        default=None,
        help='Random seed for reproducible output'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output file path (default: print to stdout)'
    )

    args = parser.parse_args()

    # Generate the data
    sql_data = generate_banking_data(
        num_accounts=args.num_accounts,
        seed=args.seed,
        output_file=args.output
    )

    # Print to stdout if no output file specified
    if not args.output:
        print(sql_data)


if __name__ == '__main__':
    main()
