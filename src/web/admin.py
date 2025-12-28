"""Django admin configuration for web application."""

from django.contrib import admin

from web.models import Account, CashAccount, CreditAccount, Transaction, Transfer


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """Admin interface for Account model."""

    list_display = ["username", "name", "surname"]
    search_fields = ["username", "name", "surname"]
    ordering = ["username"]


@admin.register(CashAccount)
class CashAccountAdmin(admin.ModelAdmin):
    """Admin interface for CashAccount model."""

    list_display = ["number", "username", "description", "availableBalance"]
    list_filter = ["username"]
    search_fields = ["number", "username", "description"]
    ordering = ["number"]


@admin.register(CreditAccount)
class CreditAccountAdmin(admin.ModelAdmin):
    """Admin interface for CreditAccount model."""

    list_display = ["number", "username", "cashAccountId", "description", "availableBalance"]
    list_filter = ["username"]
    search_fields = ["number", "username", "description"]
    ordering = ["number"]


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    """Admin interface for Transfer model."""

    list_display = ["fromAccount", "toAccount", "username", "amount", "fee", "date"]
    list_filter = ["username", "date"]
    search_fields = ["fromAccount", "toAccount", "username", "description"]
    date_hierarchy = "date"
    ordering = ["-date"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin interface for Transaction model."""

    list_display = ["number", "description", "amount", "availableBalance", "date"]
    list_filter = ["date"]
    search_fields = ["number", "description"]
    date_hierarchy = "date"
    ordering = ["-date"]
