"""Models for the insecure banking application."""

from django.db import models


class ModelSerializationMixin:
    """Mixin to add serialization capabilities to models."""

    def as_dict(self) -> dict:
        """
        Convert model instance to dictionary.

        Returns:
            Dictionary containing all model fields and values
        """
        data = {}
        for field in self._meta.fields:
            value = getattr(self, field.name)
            data[field.name] = value
        return data

    def from_dict(self, values: dict):
        """
        Populate model instance from dictionary.

        Args:
            values: Dictionary with field names as keys and values
        """
        for key, value in values.items():
            setattr(self, key, value)


class Account(models.Model):
    """
    User account model for banking application.

    Note: This model intentionally stores passwords in plain text for
    educational purposes. In production, use Django's authentication system.
    """

    username = models.CharField(primary_key=True, max_length=80)
    name = models.CharField(max_length=80)
    surname = models.CharField(max_length=80)
    password = models.CharField(max_length=80)  # Intentionally insecure

    class Meta:
        db_table = "web_account"
        verbose_name = "Account"
        verbose_name_plural = "Accounts"
        ordering = ["username"]

    def __str__(self) -> str:
        """Return string representation of account."""
        return f"{self.username} - {self.name} {self.surname}"


class CashAccount(models.Model):
    """
    Cash account model representing bank accounts.

    Note: Uses CharField for username instead of ForeignKey for educational
    purposes to demonstrate poor database design.
    """

    number = models.CharField(max_length=80, db_index=True)
    username = models.CharField(max_length=80, db_index=True)
    description = models.CharField(max_length=80)
    availableBalance = models.FloatField()  # Intentionally using camelCase

    class Meta:
        db_table = "web_cashaccount"
        verbose_name = "Cash Account"
        verbose_name_plural = "Cash Accounts"
        ordering = ["number"]

    def __str__(self) -> str:
        """Return string representation of cash account."""
        return f"Account {self.number} - {self.description} (Balance: ${self.availableBalance:.2f})"


class CreditAccount(models.Model):
    """
    Credit account model representing credit cards.

    Note: Uses IntegerField for cashAccountId instead of ForeignKey for
    educational purposes to demonstrate poor database design.
    """

    cashAccountId = models.IntegerField(db_index=True)  # Intentionally using camelCase
    number = models.CharField(max_length=80, db_index=True)
    username = models.CharField(max_length=80, db_index=True)
    description = models.CharField(max_length=80)
    availableBalance = models.FloatField()  # Intentionally using camelCase

    class Meta:
        db_table = "web_creditaccount"
        verbose_name = "Credit Account"
        verbose_name_plural = "Credit Accounts"
        ordering = ["number"]

    def __str__(self) -> str:
        """Return string representation of credit account."""
        return f"Credit Card {self.number} - {self.description} (Available: ${self.availableBalance:.2f})"


class Transfer(models.Model, ModelSerializationMixin):
    """
    Transfer model representing money transfers between accounts.

    Note: Uses CharField for accounts instead of ForeignKey for educational
    purposes to demonstrate poor database design.
    """

    fromAccount = models.CharField(max_length=80, db_index=True)  # Intentionally using camelCase
    toAccount = models.CharField(max_length=80, db_index=True)  # Intentionally using camelCase
    description = models.CharField(max_length=80)
    amount = models.FloatField()
    fee = models.FloatField(default=20)
    username = models.CharField(max_length=80, db_index=True)
    date = models.DateTimeField(db_index=True)

    class Meta:
        db_table = "web_transfer"
        verbose_name = "Transfer"
        verbose_name_plural = "Transfers"
        ordering = ["-date"]

    def __str__(self) -> str:
        """Return string representation of transfer."""
        return f"Transfer from {self.fromAccount} to {self.toAccount} - ${self.amount:.2f} on {self.date}"


class Transaction(models.Model):
    """
    Transaction model representing account activity.

    Note: Uses CharField for number instead of ForeignKey for educational
    purposes to demonstrate poor database design.
    """

    number = models.CharField(max_length=80, db_index=True)
    description = models.CharField(max_length=80)
    amount = models.FloatField()
    availableBalance = models.FloatField()  # Intentionally using camelCase
    date = models.DateTimeField(db_index=True)

    class Meta:
        db_table = "web_transaction"
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ["-date"]

    def __str__(self) -> str:
        """Return string representation of transaction."""
        return f"{self.description} - ${self.amount:.2f} on {self.date}"
