"""Transfer views."""

import json
import os
from datetime import date

from django.forms import ModelForm
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.views.generic.base import TemplateView

from apps.accounts.services import AccountService
from apps.banking.services import CashAccountService
from apps.transfers.models import Transfer
from apps.transfers.services import TransferService


def to_traces(string: str) -> str:
    """Write to traces file using os.system (intentionally vulnerable)."""
    return str(os.system(string))


class TransferForm(ModelForm):
    """Transfer form."""

    class Meta:
        """Meta options."""

        model = Transfer
        fields = ["fromAccount", "toAccount", "description", "amount", "fee"]


class TransferView(TemplateView):
    """Transfer view."""

    http_method_names = ["get", "post"]
    template_name = "newTransfer.html"

    def get(self, request, *args, **kwargs):
        """Handle GET request."""
        context = self.get_context_data(**kwargs)
        response = self.render_to_response(context)
        response.set_cookie("accountType", "Personal")
        return response

    def get_context_data(self, *args, **kwargs):
        """Get context data."""
        context = super().get_context_data(**kwargs)
        principal = self.request.user
        context["account"] = AccountService.find_users_by_username(principal.username)[0]
        context["cashAccounts"] = CashAccountService.find_cash_accounts_by_username(principal.username)
        context["transfer"] = Transfer(fee=5.0, fromAccount="", toAccount="", description="", amount=0.0)
        return context

    def post(self, request, *args, **kwargs):
        """Handle POST request."""
        account_type = request.COOKIES.get("accountType")
        if request.path.endswith("/confirm"):
            action = request.POST["action"]
            if "pendingTransfer" in request.session and action == "confirm":
                transfer = Transfer()
                transfer.from_dict(json.loads(request.session["pendingTransfer"]))
                del request.session["pendingTransfer"]
                return self.transfer_confirmation(request, transfer, account_type)
            return redirect("/transfer")
        transfer_form = TransferForm(request.POST)
        transfer_form.is_valid()  # ensure model is bound
        transfer = transfer_form.instance
        to_traces(
            f"echo {transfer.fromAccount} to account {transfer.toAccount} "
            f"accountType:{account_type}>traces.txt"
        )
        if account_type == "Personal":
            return self.transfer_check(request, transfer)
        return self.transfer_confirmation(request, transfer, account_type)

    def transfer_check(self, request, transfer) -> HttpResponse:
        """Check transfer before confirmation."""
        request.session["pendingTransfer"] = json.dumps(transfer.as_dict())
        principal = self.request.user
        accounts = AccountService.find_users_by_username(principal.username)
        template = loader.get_template("transferCheck.html")
        context = {
            "account": accounts[0],
            "transferbean": transfer,
            "operationConfirm": dict(),
        }
        return HttpResponse(template.render(context, request))

    def transfer_confirmation(self, request, transfer, account_type: str) -> HttpResponse:
        """Confirm and execute transfer."""
        principal = self.request.user
        cash_accounts = CashAccountService.find_cash_accounts_by_username(principal.username)
        accounts = AccountService.find_users_by_username(principal.username)
        aux = transfer.amount
        if aux == 0.0:
            template = loader.get_template("newTransfer.html")
            context = {
                "account": accounts[0],
                "cashAccounts": cash_accounts,
                "transfer": transfer,
                "error": True,
            }
            return HttpResponse(template.render(context, request))
        transfer.username = principal.username
        transfer.date = date.today()
        transfer.amount = round(transfer.amount, 2)
        transfer.fee = round((transfer.amount * transfer.fee) / 100, 2)
        TransferService.createNewTransfer(transfer)
        template = loader.get_template("transferConfirmation.html")
        context = {
            "transferbean": transfer,
            "account": accounts[0],
            "accountType": account_type,
        }
        return HttpResponse(template.render(context, request))
