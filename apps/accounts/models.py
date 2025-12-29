"""Account models."""

from django.db import models


class Account(models.Model):
    """User account model."""

    username = models.CharField(primary_key=True, max_length=80)
    name = models.CharField(max_length=80)
    surname = models.CharField(max_length=80)
    password = models.CharField(max_length=80)

    class Meta:
        """Meta options."""

        db_table = "web_account"
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    def __str__(self):
        """String representation."""
        return f"{self.name} {self.surname} ({self.username})"
