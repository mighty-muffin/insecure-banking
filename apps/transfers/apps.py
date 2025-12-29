"""Transfers app configuration."""

from django.apps import AppConfig


class TransfersConfig(AppConfig):
    """Transfers app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.transfers"
    verbose_name = "Transfers"
