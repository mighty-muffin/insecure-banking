"""
Views for the insecure banking web application.

Note: This module contains intentional security vulnerabilities for educational
purposes, including:
- Pickle deserialization vulnerabilities
- Command injection vulnerabilities
- Weak cryptography (DES)
- Path traversal vulnerabilities

In production code, never use these patterns.
"""

import base64
import json
import logging
import os
import pickle
from datetime import date
from typing import Any, Optional

from Crypto.Cipher import DES
from Crypto.Util.Padding import pad
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.views.generic.base import TemplateView, View

from web.forms import TransferForm
from web.models import Transfer
from web.services import (
    AccountService,
    ActivityService,
    CashAccountService,
    CreditAccountService,
    StorageService,
    TransferService,
)

logger = logging.getLogger(__name__)
storage_service = StorageService()
secretKey = bytes("01234567", "UTF-8")  # Intentionally weak key
checksum = [""]  # Global state for certificate validation
resources = os.path.join(settings.BASE_DIR, "src", "web", "static", "resources")


class Trusted:
    """
    Trusted object for certificate serialization.

    Note: This class is part of an intentional pickle deserialization
    vulnerability demonstration.
    """

    username: Optional[str] = None

    def __init__(self, username: str):
        """
        Initialize trusted object.

        Args:
            username: Username to store in the certificate
        """
        self.username = username


class Untrusted(Trusted):
    """
    Untrusted object that executes code when unpickled.

    WARNING: This class demonstrates an insecure deserialization vulnerability.
    Never implement __reduce__ to execute arbitrary commands in production code.
    """

    def __init__(self, username: str):
        """
        Initialize untrusted object.

        Args:
            username: Username to store in the certificate
        """
        super().__init__(username)

    def __reduce__(self):
        """
        Return a callable and arguments for unpickling.

        WARNING: This implementation executes os.system when unpickled,
        demonstrating a critical security vulnerability.

        Returns:
            Tuple of callable and arguments for pickle
        """
        return os.system, ("ls -lah",)


def get_file_checksum(data: bytes) -> str:
    """
    Calculate checksum for file data using DES encryption.

    WARNING: This function uses weak DES encryption and is intentionally
    insecure for educational purposes. In production, use modern algorithms
    like SHA-256 or bcrypt.

    Args:
        data: Binary data to checksum

    Returns:
        Base64-encoded checksum string
    """
    (dk, iv) = (secretKey, secretKey)
    crypter = DES.new(dk, DES.MODE_CBC, iv)
    padded = pad(data, DES.block_size)
    encrypted = crypter.encrypt(padded)
    return base64.b64encode(encrypted).decode("UTF-8")


def to_traces(string: str) -> str:
    """
    Execute system command and return result.

    WARNING: This function is intentionally vulnerable to command injection.
    Never use os.system with user input in production code.

    Args:
        string: Command string to execute

    Returns:
        String representation of command exit code
    """
    return str(os.system(string))


class LoginView(TemplateView):
    """
    View for user login.

    Handles both GET (display login form) and POST (process login) requests.
    """

    http_method_names = ["get", "post"]
    template_name = "login.html"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Process login form submission.

        Args:
            request: HTTP request with login credentials

        Returns:
            Redirect to dashboard on success, or login page with error
        """
        user = authenticate(request=request)
        if user is None:
            template = loader.get_template("login.html")
            context = {"authenticationFailure": True}
            return HttpResponse(template.render(context, request))
        login(request, user)
        return redirect("/dashboard")


class LogoutView(View):
    """View for user logout."""

    http_method_names = ["get"]

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Process logout request.

        Args:
            request: HTTP request

        Returns:
            Redirect to login page
        """
        logout(request)
        return redirect("/login")


class AdminView(TemplateView):
    """
    Admin view for managing user accounts.

    Displays all user accounts and their information.
    """

    http_method_names = ["get"]
    template_name = "admin.html"

    def get_context_data(self, *args, **kwargs) -> dict:
        """
        Prepare context data for admin page.

        Returns:
            Dictionary with account and accounts list
        """
        context = super(AdminView, self).get_context_data(**kwargs)
        principal = self.request.user
        context["account"] = AccountService.find_users_by_username(principal.username)[0]
        context["accounts"] = AccountService.find_all_users()
        return context


class ActivityView(TemplateView):
    """
    View for displaying account activity and transactions.

    Shows transaction history for a specific cash account.
    """

    http_method_names = ["get", "post"]
    template_name = "accountActivity.html"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handle POST request for activity filtering.

        Args:
            request: HTTP request with account number filter

        Returns:
            Rendered activity page with filtered transactions
        """
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, *args, **kwargs) -> dict:
        """
        Prepare context data for activity page.

        Returns:
            Dictionary with account details and transaction history
        """
        context = super(ActivityView, self).get_context_data(**kwargs)
        principal = self.request.user
        account = AccountService.find_users_by_username(principal.username)[0]
        cash_accounts = CashAccountService.find_cash_accounts_by_username(principal.username)
        if "account" in self.request.resolver_match.kwargs:
            account_number = self.request.resolver_match.kwargs["account"]
        elif "number" in self.request.POST:
            account_number = self.request.POST["number"]
        else:
            account_number = cash_accounts[0].number
        first_cash_account_transfers = ActivityService.find_transactions_by_cash_account_number(account_number)
        reverse_fist_cash_account_transfers = list(reversed(first_cash_account_transfers))
        context["account"] = account
        context["cashAccounts"] = cash_accounts
        context["cashAccount"] = dict()
        context["firstCashAccountTransfers"] = reverse_fist_cash_account_transfers
        context["actualCashAccountNumber"] = account_number
        return context


class ActivityCreditView(TemplateView):
    """
    View for displaying credit card activity.

    Shows transaction history for a specific credit card.
    """

    http_method_names = ["get"]
    template_name = "creditActivity.html"

    def get_context_data(self, *args, **kwargs) -> dict:
        """
        Prepare context data for credit activity page.

        Returns:
            Dictionary with account and credit card details
        """
        context = super(ActivityCreditView, self).get_context_data(**kwargs)
        principal = self.request.user
        number = self.request.GET["number"]
        account = AccountService.find_users_by_username(principal.username)[0]
        context["account"] = account
        context["actualCreditCardNumber"] = number
        return context


class DashboardView(TemplateView):
    """
    Main dashboard view.

    Displays user's cash and credit accounts overview.
    """

    http_method_names = ["get"]
    template_name = "dashboard.html"

    def get_context_data(self, *args, **kwargs) -> dict:
        """
        Prepare context data for dashboard.

        Returns:
            Dictionary with user account and financial accounts
        """
        context = super(DashboardView, self).get_context_data(**kwargs)
        principal = self.request.user
        context["account"] = AccountService.find_users_by_username(principal.username)[0]
        context["cashAccounts"] = CashAccountService.find_cash_accounts_by_username(principal.username)
        context["creditAccounts"] = CreditAccountService.find_credit_accounts_by_username(principal.username)
        return context


class UserDetailView(TemplateView):
    """
    View for displaying user profile details.

    Shows user information and credit card details.
    """

    http_method_names = ["get"]
    template_name = "userDetail.html"

    def get_context_data(self, *args, **kwargs) -> dict:
        """
        Prepare context data for user detail page.

        Returns:
            Dictionary with user account and credit card information
        """
        context = super(UserDetailView, self).get_context_data(**kwargs)
        principal = self.request.user
        accounts = AccountService.find_users_by_username(principal.username)
        context["account"] = accounts[0]
        context["creditAccounts"] = CreditAccountService.find_credit_accounts_by_username(principal.username)
        context["accountMalicious"] = accounts[0]
        return context


class AvatarView(View):
    """
    View for serving user avatar images.

    WARNING: This view is intentionally vulnerable to path traversal.
    In production, always validate and sanitize file paths.
    """

    http_method_names = ["get"]

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Serve avatar image.

        WARNING: Allows arbitrary file access through path traversal.

        Args:
            request: HTTP request with 'image' parameter

        Returns:
            Image file content
        """
        image = request.GET.get("image")
        file = image if storage_service.exists(image) else "avatar.png"
        return HttpResponse(storage_service.load(file), content_type="image/png")


class AvatarUpdateView(View):
    """
    View for uploading and updating user avatar.

    Allows users to upload a new profile picture.
    """

    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handle avatar upload.

        Args:
            request: HTTP request with image file

        Returns:
            Redirect to user detail page
        """
        image = request.FILES["imageFile"]
        principal = self.request.user
        storage_service.save(image.file.read(), principal.username + ".png")
        return redirect("/dashboard/userDetail?username=" + principal.username)


class CertificateDownloadView(View):
    """
    View for downloading serialized certificate.

    WARNING: Uses pickle serialization which is inherently insecure.
    """

    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Generate and download certificate.

        Args:
            request: HTTP request

        Returns:
            Pickled certificate as download
        """
        certificate = pickle.dumps(Trusted("this is safe"))
        principal = self.request.user
        account = AccountService.find_users_by_username(principal.username)[0]
        file_name = f"attachment;Certificate_={account.name}"
        return HttpResponse(
            certificate,
            content_type="application/octet-stream",
            headers={"Content-Disposition": file_name},
        )


class MaliciousCertificateDownloadView(View):
    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        certificate = pickle.dumps(Untrusted("this is not safe"))
        checksum[0] = get_file_checksum(certificate)
        principal = self.request.user
        account = AccountService.find_users_by_username(principal.username)[0]
        file_name = f"attachment;MaliciousCertificate_={account.name}"
        return HttpResponse(
            certificate,
            content_type="application/octet-stream",
            headers={"Content-Disposition": file_name},
        )


class MaliciousCertificateDownloadView(View):
    """
    View for downloading malicious certificate.

    WARNING: This demonstrates insecure deserialization vulnerability.
    Downloads a certificate that executes code when unpickled.
    """

    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Generate and download malicious certificate.

        WARNING: This certificate contains executable code.

        Args:
            request: HTTP request

        Returns:
            Malicious pickled certificate as download
        """
        certificate = pickle.dumps(Untrusted("this is not safe"))
        checksum[0] = get_file_checksum(certificate)
        principal = self.request.user
        account = AccountService.find_users_by_username(principal.username)[0]
        file_name = f"attachment;MaliciousCertificate_={account.name}"
        return HttpResponse(
            certificate,
            content_type="application/octet-stream",
            headers={"Content-Disposition": file_name},
        )


class NewCertificateView(View):
    """
    View for uploading and processing certificates.

    WARNING: This view unsafely deserializes uploaded files using pickle.
    Never use pickle.loads on untrusted data in production.
    """

    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Process uploaded certificate.

        WARNING: Uses pickle.loads on uploaded data, which is extremely dangerous.

        Args:
            request: HTTP request with file upload

        Returns:
            Success or error message
        """
        if "file" not in request.FILES:
            return HttpResponse("<p>No file uploaded</p>")

        certificate = request.FILES["file"]
        data = certificate.file.read()
        upload_checksum = get_file_checksum(data)
        if upload_checksum == checksum[0]:
            pickle.loads(data)  # Intentionally dangerous
            return HttpResponse(f"<p>File '{certificate}' uploaded successfully</p>", content_type="text/plain")
        return HttpResponse(f"<p>File '{certificate}' not processed, only previously downloaded malicious file is allowed</p>")


class CreditCardImageView(View):
    """
    View for serving credit card images.

    WARNING: This view is vulnerable to path traversal attacks.
    In production, always validate file paths and use secure file serving.
    """

    http_method_names = ["get"]

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Serve credit card image.

        WARNING: Vulnerable to path traversal.

        Args:
            request: HTTP request with 'url' parameter

        Returns:
            Image file content
        """
        image = request.GET.get("url")
        filename, file_extension = os.path.splitext(image)
        name = filename + file_extension
        with open(os.path.join(resources, name), "rb") as fh:
            data = fh.read()
            return HttpResponse(
                data,
                content_type="image/png",
                headers={"Content-Disposition": f'attachment; filename="{name}"'},
            )


class TransferView(TemplateView):
    """
    View for creating money transfers.

    Handles display of transfer form and processing of transfers.
    WARNING: Contains command injection vulnerability in transfer processing.
    """

    http_method_names = ["get", "post"]
    template_name = "newTransfer.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Display transfer form.

        Args:
            request: HTTP request

        Returns:
            Rendered transfer form with cookie set
        """
        context = self.get_context_data(**kwargs)
        response = self.render_to_response(context)
        response.set_cookie("accountType", "Personal")
        return response

    def get_context_data(self, *args, **kwargs) -> dict:
        """
        Prepare context data for transfer form.

        Returns:
            Dictionary with user accounts and transfer object
        """
        context = super(TransferView, self).get_context_data(**kwargs)
        principal = self.request.user
        context["account"] = AccountService.find_users_by_username(principal.username)[0]
        context["cashAccounts"] = CashAccountService.find_cash_accounts_by_username(principal.username)
        context["transfer"] = Transfer(fee=5.0, fromAccount="", toAccount="", description="", amount=0.0)
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Process transfer form submission.

        WARNING: Contains command injection vulnerability via to_traces function.

        Args:
            request: HTTP request with transfer data

        Returns:
            Redirect, confirmation page, or error page
        """
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
        to_traces(f"echo {transfer.fromAccount} to account {transfer.toAccount} accountType:{account_type}>traces.txt")
        if account_type == "Personal":
            return self.transfer_check(request, transfer)
        return self.transfer_confirmation(request, transfer, account_type)

    def transfer_check(self, request: HttpRequest, transfer: Transfer) -> HttpResponse:
        """
        Display transfer confirmation page.

        Args:
            request: HTTP request
            transfer: Transfer object to confirm

        Returns:
            Transfer confirmation page
        """
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

    def transfer_confirmation(self, request: HttpRequest, transfer: Transfer, account_type: str) -> HttpResponse:
        """
        Process and confirm transfer.

        Args:
            request: HTTP request
            transfer: Transfer object to process
            account_type: Type of account (Personal/Business)

        Returns:
            Transfer confirmation page or error page
        """
        principal = self.request.user
        cash_accounts = CashAccountService.find_cash_accounts_by_username(principal.username)
        accounts = AccountService.find_users_by_username(principal.username)
        aux = transfer.amount
        if aux is None or aux == 0.0:
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
