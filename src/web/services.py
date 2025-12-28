"""
Service layer for business logic.

Note: This module intentionally uses raw SQL queries for educational purposes
to demonstrate SQL injection vulnerabilities. In production, always use Django ORM
or parameterized queries.
"""

import os
from typing import Optional

from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.db import connection, transaction

from web.models import (
    Account,
    CashAccount,
    CreditAccount,
    Transaction,
    Transfer,
)


class StorageService:
    """
    Service for handling file storage operations.

    Manages avatar images and other static resources.
    """

    folder = os.path.join(settings.BASE_DIR, "src", "web", "static", "resources", "avatars")

    def exists(self, file_name: str) -> bool:
        """
        Check if a file exists in storage.

        Args:
            file_name: Name of the file to check

        Returns:
            True if file exists, False otherwise
        """
        file = os.path.join(self.folder, file_name)
        return os.path.exists(file)

    def load(self, file_name: str) -> bytes:
        """
        Load file contents from storage.

        Args:
            file_name: Name of the file to load

        Returns:
            File contents as bytes
        """
        file = os.path.join(self.folder, file_name)
        with open(file, "rb") as fh:
            return fh.read()

    def save(self, data: bytes, file_name: str) -> None:
        """
        Save data to a file in storage.

        Args:
            data: Binary data to save
            file_name: Name of the file to save to
        """
        file = os.path.join(self.folder, file_name)
        with open(file, "wb") as fh:
            fh.write(data)


class AccountService(BaseBackend):
    """
    Service for account management and authentication.

    Note: This service intentionally implements insecure authentication
    for educational purposes. In production, use Django's built-in
    authentication system.
    """

    def authenticate(self, request, username: Optional[str] = None, password: Optional[str] = None) -> Optional[User]:
        """
        Authenticate a user with username and password.

        Args:
            request: HTTP request object
            username: Username (optional, extracted from request if not provided)
            password: Password (optional, extracted from request if not provided)

        Returns:
            Authenticated User object or None if authentication fails
        """
        username = request.POST.get("username")
        password = request.POST.get("password")
        if not username or not password:
            return None
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

    def get_user(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User's primary key

        Returns:
            User object or None if not found
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def find_users_by_username_and_password(username: str, password: str) -> list[Account]:
        """
        Find accounts by username and password.

        WARNING: This method is intentionally vulnerable to SQL injection
        for educational purposes. Never use string concatenation in SQL queries.

        Args:
            username: Account username
            password: Account password

        Returns:
            List of matching Account objects
        """
        sql = "select * from web_account where username='" + username + "' AND password='" + password + "'"
        return Account.objects.raw(sql)

    @staticmethod
    def find_users_by_username(username: str) -> list[Account]:
        """
        Find accounts by username.

        WARNING: This method is intentionally vulnerable to SQL injection
        for educational purposes. Never use string concatenation in SQL queries.

        Args:
            username: Account username

        Returns:
            List of matching Account objects
        """
        sql = "select * from web_account where username='" + username + "'"
        return Account.objects.raw(sql)

    @staticmethod
    def find_all_users() -> list[Account]:
        """
        Find all user accounts.

        Returns:
            List of all Account objects
        """
        sql = "select * from web_account"
        return Account.objects.raw(sql)


class CashAccountService:
    """
    Service for cash account management.

    Note: This service intentionally uses raw SQL queries for educational
    purposes to demonstrate SQL injection vulnerabilities.
    """

    @staticmethod
    def find_cash_accounts_by_username(username: str) -> list[CashAccount]:
        """
        Find cash accounts by username.

        WARNING: This method is intentionally vulnerable to SQL injection
        for educational purposes.

        Args:
            username: Account owner's username

        Returns:
            List of matching CashAccount objects
        """
        sql = "select * from web_cashaccount  where username='" + username + "'"
        return CashAccount.objects.raw(sql)

    @staticmethod
    def get_from_account_actual_amount(account: str) -> float:
        """
        Get current balance for a cash account.

        WARNING: This method is intentionally vulnerable to SQL injection
        for educational purposes.

        Args:
            account: Account number

        Returns:
            Current account balance
        """
        sql = "SELECT availableBalance FROM web_cashaccount WHERE number = '" + account + "'"
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchone()
            return row[0]

    @staticmethod
    def get_id_from_number(account: str) -> int:
        """
        Get account ID from account number.

        WARNING: This method is intentionally vulnerable to SQL injection
        for educational purposes.

        Args:
            account: Account number

        Returns:
            Account ID
        """
        sql = "SELECT id FROM web_cashaccount WHERE number = '" + account + "'"
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchone()
            return row[0]


class CreditAccountService:
    """
    Service for credit account management.

    Note: This service intentionally uses raw SQL queries for educational
    purposes to demonstrate SQL injection vulnerabilities.
    """

    @staticmethod
    def find_credit_accounts_by_username(username: str) -> list[CreditAccount]:
        """
        Find credit accounts by username.

        WARNING: This method is intentionally vulnerable to SQL injection
        for educational purposes.

        Args:
            username: Account owner's username

        Returns:
            List of matching CreditAccount objects
        """
        sql = "select * from web_creditaccount  where username='" + username + "'"
        return CreditAccount.objects.raw(sql)

    @staticmethod
    def update_credit_account(cashAccountId: int, round: float) -> None:
        """
        Update credit account balance.

        WARNING: This method is intentionally vulnerable to SQL injection
        for educational purposes.

        Args:
            cashAccountId: Cash account ID
            round: New balance amount
        """
        sql = (
            "UPDATE web_creditaccount SET availableBalance='"
            + str(round)
            + "' WHERE cashAccountId ='"
            + str(cashAccountId)
            + "'"
        )
        with connection.cursor() as cursor:
            cursor.execute(sql)


class ActivityService:
    """
    Service for transaction activity management.

    Note: This service intentionally uses raw SQL queries for educational
    purposes to demonstrate SQL injection vulnerabilities.
    """

    @staticmethod
    def find_transactions_by_cash_account_number(number: str) -> list[Transaction]:
        """
        Find transactions by account number.

        WARNING: This method is intentionally vulnerable to SQL injection
        for educational purposes.

        Args:
            number: Account number

        Returns:
            List of matching Transaction objects
        """
        sql = "SELECT * FROM web_transaction WHERE number = '" + number + "'"
        return Transaction.objects.raw(sql)

    @staticmethod
    def insert_new_activity(date, description: str, number: str, amount: float, avaiable_balance: float) -> None:
        """
        Insert a new transaction activity.

        Args:
            date: Transaction date
            description: Transaction description
            number: Account number
            amount: Transaction amount
            avaiable_balance: Available balance after transaction
        """
        sql = "INSERT INTO web_transaction (date, description, number, amount, availablebalance) VALUES (%s, %s, %s, %s, %s)"
        with connection.cursor() as cursor:
            cursor.execute(sql, [date, description, number, amount, avaiable_balance])


class TransferService:
    """
    Service for managing money transfers.

    Handles transfer creation and associated account balance updates.
    """

    @staticmethod
    def insert_transfer(transfer: Transfer) -> None:
        """
        Insert a new transfer record.

        Args:
            transfer: Transfer object to insert
        """
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

    @staticmethod
    @transaction.atomic
    def createNewTransfer(transfer: Transfer) -> None:
        """
        Create a new transfer and update associated accounts.

        This method:
        1. Inserts the transfer record
        2. Updates sender's account balance
        3. Records transfer fee activity
        4. Updates recipient's account balance
        5. Records all activity transactions

        Args:
            transfer: Transfer object to process

        Note: Uses @transaction.atomic to ensure all operations complete
        successfully or rollback on error.
        """
        TransferService.insert_transfer(transfer)

        actual_amount = CashAccountService.get_from_account_actual_amount(transfer.fromAccount)
        amount_total = actual_amount - (transfer.amount + transfer.fee)
        amount = actual_amount - transfer.amount
        amount_with_fees = amount - transfer.fee
        cash_account_id = CashAccountService.get_id_from_number(transfer.fromAccount)
        CreditAccountService.update_credit_account(cash_account_id, round(amount_total, 2))
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
