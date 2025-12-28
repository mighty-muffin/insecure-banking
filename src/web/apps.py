"""Django app configuration for the web application."""

from django.apps import AppConfig


class WebConfig(AppConfig):
    """Configuration for the web application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "web"
    verbose_name = "Insecure Banking Web Application"
