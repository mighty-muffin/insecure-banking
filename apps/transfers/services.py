"""Transfer services."""

from django.db import connection, transaction

from apps.transfers.models import Transfer
from apps.banking.services import (
    CashAccountService,
    CreditAccountService,
    ActivityService,
)


class TransferService:
    """Service for transfer operations."""

    @staticmethod
    def insert_transfer(transfer: Transfer):
        """Insert transfer into database."""
        sql = (
            "INSERT INTO web_transfer "
            "(fromAccount, toAccount, description, amount, fee, username, date) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        with connection.cursor() as cursor:
            cursor.execute(
                sql,
                [
                    transfer.fromAccount,
                    transfer.toAccount,
                    transfer.description,
                    transfer.amount,
                    transfer.fee,
                    transfer.username,
                    transfer.date,
                ],
            )

    @staticmethod
    @transaction.atomic
    def createNewTransfer(transfer: Transfer):
        """Create a new transfer and update account balances."""
        TransferService.insert_transfer(transfer)

        actual_amount = CashAccountService.get_from_account_actual_amount(transfer.fromAccount)
        amount_total = actual_amount - (transfer.amount + transfer.fee)
        amount = actual_amount - transfer.amount
        amount_with_fees = amount - transfer.fee
        cash_account_id = CashAccountService.get_id_from_number(transfer.fromAccount)
        CreditAccountService.update_credit_account(cash_account_id, round(amount_total, 2))
        desc = transfer.description if len(transfer.description) <= 12 else transfer.description[0:12]
        ActivityService.insert_new_activity(
            transfer.date,
            f"TRANSFER: {desc}",
            transfer.fromAccount,
            -round(transfer.amount, 2),
            round(amount, 2),
        )
        ActivityService.insert_new_activity(
            transfer.date,
            "TRANSFER FEE",
            transfer.fromAccount,
            -round(transfer.fee, 2),
            round(amount_with_fees, 2),
        )

        to_cash_account_id = CashAccountService.get_id_from_number(transfer.toAccount)
        to_actual_amount = CashAccountService.get_from_account_actual_amount(transfer.toAccount)
        to_amount_total = to_actual_amount + transfer.amount
        CreditAccountService.update_credit_account(to_cash_account_id, round(to_amount_total, 2))
        ActivityService.insert_new_activity(
            transfer.date,
            f"TRANSFER: ${desc}",
            transfer.toAccount,
            round(transfer.amount, 2),
            round(to_amount_total, 2),
        )
