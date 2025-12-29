"""Banking services."""

from django.db import connection

from apps.banking.models import CashAccount, CreditAccount, Transaction


class CashAccountService:
    """Service for cash account operations."""

    @staticmethod
    def find_cash_accounts_by_username(username: str) -> list[CashAccount]:
        """Find cash accounts by username using raw SQL (intentionally vulnerable)."""
        sql = f"select * from web_cashaccount  where username='{username}'"
        return CashAccount.objects.raw(sql)

    @staticmethod
    def get_from_account_actual_amount(account: str) -> float:
        """Get account balance using raw SQL (intentionally vulnerable)."""
        sql = f"SELECT availableBalance FROM web_cashaccount WHERE number = '{account}'"
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchone()
            return row[0]

    @staticmethod
    def get_id_from_number(account: str) -> int:
        """Get account ID from number using raw SQL (intentionally vulnerable)."""
        sql = f"SELECT id FROM web_cashaccount WHERE number = '{account}'"
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchone()
            return row[0]


class CreditAccountService:
    """Service for credit account operations."""

    @staticmethod
    def find_credit_accounts_by_username(username: str) -> list[CreditAccount]:
        """Find credit accounts by username using raw SQL (intentionally vulnerable)."""
        sql = f"select * from web_creditaccount  where username='{username}'"
        return CreditAccount.objects.raw(sql)

    @staticmethod
    def update_credit_account(cashAccountId: int, round: float):
        """Update credit account using raw SQL (intentionally vulnerable)."""
        sql = (
            f"UPDATE web_creditaccount SET availableBalance='{round}' "
            f"WHERE cashAccountId ='{cashAccountId}'"
        )
        with connection.cursor() as cursor:
            cursor.execute(sql)


class ActivityService:
    """Service for activity/transaction operations."""

    @staticmethod
    def find_transactions_by_cash_account_number(number: str) -> list[Transaction]:
        """Find transactions by account number using raw SQL (intentionally vulnerable)."""
        sql = f"SELECT * FROM web_transaction WHERE number = '{number}'"
        return Transaction.objects.raw(sql)

    @staticmethod
    def insert_new_activity(date, description: str, number: str, amount: float, avaiable_balance: float):
        """Insert new activity/transaction."""
        sql = (
            "INSERT INTO web_transaction "
            "(date, description, number, amount, availablebalance) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        with connection.cursor() as cursor:
            cursor.execute(sql, [date, description, number, amount, avaiable_balance])
