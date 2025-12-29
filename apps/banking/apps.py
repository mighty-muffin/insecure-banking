"""Banking app configuration."""

from django.apps import AppConfig


class BankingConfig(AppConfig):
    """Banking app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.banking"
    verbose_name = "Banking"
