"""Banking models."""

from django.db import models


class CashAccount(models.Model):
    """Cash account model."""

    number = models.CharField(max_length=80)
    username = models.CharField(max_length=80)
    description = models.CharField(max_length=80)
    availableBalance = models.FloatField()

    class Meta:
        """Meta options."""

        db_table = "web_cashaccount"
        verbose_name = "Cash Account"
        verbose_name_plural = "Cash Accounts"

    def __str__(self):
        """String representation."""
        return f"{self.number} - {self.description}"


class CreditAccount(models.Model):
    """Credit account model."""

    cashAccountId = models.IntegerField()
    number = models.CharField(max_length=80)
    username = models.CharField(max_length=80)
    description = models.CharField(max_length=80)
    availableBalance = models.FloatField()

    class Meta:
        """Meta options."""

        db_table = "web_creditaccount"
        verbose_name = "Credit Account"
        verbose_name_plural = "Credit Accounts"

    def __str__(self):
        """String representation."""
        return f"{self.number} - {self.description}"


class Transaction(models.Model):
    """Transaction model."""

    number = models.CharField(max_length=80)
    description = models.CharField(max_length=80)
    amount = models.FloatField()
    availableBalance = models.FloatField()
    date = models.DateTimeField()

    class Meta:
        """Meta options."""

        db_table = "web_transaction"
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        """String representation."""
        return f"{self.number} - {self.description} ({self.amount})"
