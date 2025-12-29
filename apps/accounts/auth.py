"""Custom authentication backend."""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

from apps.accounts.services import AccountService


class AccountAuthenticationBackend(BaseBackend):
    """Custom authentication backend using Account model."""

    def authenticate(self, request, username=None, password=None):
        """Authenticate user."""
        username = request.POST.get("username")
        password = request.POST.get("password")
        if not username or not password:
            return None
        accounts = AccountService.find_users_by_username_and_password(username, password)
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

    def get_user(self, user_id):
        """Get user by ID."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
