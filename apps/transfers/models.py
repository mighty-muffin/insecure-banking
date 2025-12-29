"""Transfer models."""

from django.db import models


class ModelSerializationMixin:
    """Mixin for model serialization."""

    def as_dict(self) -> dict:
        """Convert model to dictionary."""
        data = {}
        for field in self._meta.fields:
            value = getattr(self, field.name)
            data[field.name] = value
        return data

    def from_dict(self, values: dict):
        """Load model from dictionary."""
        for key, value in values.items():
            setattr(self, key, value)


class Transfer(models.Model, ModelSerializationMixin):
    """Transfer model."""

    fromAccount = models.CharField(max_length=80)
    toAccount = models.CharField(max_length=80)
    description = models.CharField(max_length=80)
    amount = models.FloatField()
    fee = models.FloatField(default=20)
    username = models.CharField(max_length=80)
    date = models.DateTimeField()

    class Meta:
        """Meta options."""

        db_table = "web_transfer"
        verbose_name = "Transfer"
        verbose_name_plural = "Transfers"

    def __str__(self):
        """String representation."""
        return f"{self.fromAccount} -> {self.toAccount}: {self.amount}"
