"""Account services."""

from django.db import connection

from apps.accounts.models import Account


class AccountService:
    """Service for account-related operations."""

    @staticmethod
    def find_users_by_username_and_password(username: str, password: str) -> list[Account]:
        """Find users by username and password using raw SQL (intentionally vulnerable)."""
        sql = f"select * from web_account where username='{username}' AND password='{password}'"
        return Account.objects.raw(sql)

    @staticmethod
    def find_users_by_username(username: str) -> list[Account]:
        """Find users by username using raw SQL (intentionally vulnerable)."""
        sql = f"select * from web_account where username='{username}'"
        return Account.objects.raw(sql)

    @staticmethod
    def find_all_users() -> list[Account]:
        """Find all users using raw SQL."""
        sql = "select * from web_account"
        return Account.objects.raw(sql)
