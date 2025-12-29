"""Banking views."""

import os
import pickle
from typing import Any

from Crypto.Cipher import DES
from Crypto.Util.Padding import pad
import base64
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic.base import TemplateView, View

from apps.accounts.services import AccountService
from apps.banking.services import (
    ActivityService,
    CashAccountService,
    CreditAccountService,
)


class StorageService:
    """Service for file storage operations."""

    folder = os.path.join(settings.BASE_DIR, "static", "resources", "avatars")

    def exists(self, file_name: str) -> bool:
        """Check if file exists."""
        file = os.path.join(self.folder, file_name)
        return os.path.exists(file)

    def load(self, file_name: str):
        """Load file content."""
        file = os.path.join(self.folder, file_name)
        with open(file, "rb") as fh:
            return fh.read()

    def save(self, data: bytes, file_name: str):
        """Save file content."""
        file = os.path.join(self.folder, file_name)
        with open(file, "wb") as fh:
            fh.write(data)


class Trusted:
    """Trusted serialization class."""

    username: str | None = None

    def __init__(self, username: str):
        """Initialize trusted object."""
        self.username = username


class Untrusted(Trusted):
    """Untrusted serialization class (intentionally vulnerable)."""

    def __init__(self, username: str):
        """Initialize untrusted object."""
        super().__init__(username)

    def __reduce__(self):
        """Reduce method for pickling (intentionally vulnerable)."""
        return os.system, ("ls -lah",)


# Module-level variables
storage_service = StorageService()
secretKey = bytes("01234567", "UTF-8")
checksum = [""]
resources = os.path.join(settings.BASE_DIR, "static", "resources")


def get_file_checksum(data: bytes) -> str:
    """Get file checksum using DES encryption (intentionally weak)."""
    (dk, iv) = (secretKey, secretKey)
    crypter = DES.new(dk, DES.MODE_CBC, iv)
    padded = pad(data, DES.block_size)
    encrypted = crypter.encrypt(padded)
    return base64.b64encode(encrypted).decode("UTF-8")


def to_traces(string: str) -> str:
    """Write to traces file using os.system (intentionally vulnerable)."""
    return str(os.system(string))


class ActivityView(TemplateView):
    """Activity view."""

    http_method_names = ["get", "post"]
    template_name = "accountActivity.html"

    def post(self, request, *args, **kwargs):
        """Handle POST request."""
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, *args, **kwargs):
        """Get context data."""
        context = super().get_context_data(**kwargs)
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
    """Activity credit view."""

    http_method_names = ["get"]
    template_name = "creditActivity.html"

    def get_context_data(self, *args, **kwargs):
        """Get context data."""
        context = super().get_context_data(**kwargs)
        principal = self.request.user
        number = self.request.GET["number"]
        account = AccountService.find_users_by_username(principal.username)[0]
        context["account"] = account
        context["actualCreditCardNumber"] = number
        return context


class DashboardView(TemplateView):
    """Dashboard view."""

    http_method_names = ["get"]
    template_name = "dashboard.html"

    def get_context_data(self, *args, **kwargs):
        """Get context data."""
        context = super().get_context_data(**kwargs)
        principal = self.request.user
        context["account"] = AccountService.find_users_by_username(principal.username)[0]
        context["cashAccounts"] = CashAccountService.find_cash_accounts_by_username(principal.username)
        context["creditAccounts"] = CreditAccountService.find_credit_accounts_by_username(principal.username)
        return context


class UserDetailView(TemplateView):
    """User detail view."""

    http_method_names = ["get"]
    template_name = "userDetail.html"

    def get_context_data(self, *args, **kwargs):
        """Get context data."""
        context = super().get_context_data(**kwargs)
        principal = self.request.user
        accounts = AccountService.find_users_by_username(principal.username)
        context["account"] = accounts[0]
        context["creditAccounts"] = CreditAccountService.find_credit_accounts_by_username(principal.username)
        context["accountMalicious"] = accounts[0]
        return context


class AvatarView(View):
    """Avatar view."""

    http_method_names = ["get"]

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Handle GET request."""
        image = request.GET.get("image")
        file = image if storage_service.exists(image) else "avatar.png"
        return HttpResponse(storage_service.load(file), content_type="image/png")


class AvatarUpdateView(View):
    """Avatar update view."""

    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        """Handle POST request."""
        image = request.FILES["imageFile"]
        principal = self.request.user
        storage_service.save(image.file.read(), principal.username + ".png")
        return redirect("/dashboard/userDetail?username=" + principal.username)


class CertificateDownloadView(View):
    """Certificate download view."""

    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Handle POST request."""
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
    """Malicious certificate download view (intentionally vulnerable)."""

    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Handle POST request."""
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
    """New certificate upload view (intentionally vulnerable)."""

    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Handle POST request."""
        if "file" not in request.FILES:
            return HttpResponse("<p>No file uploaded</p>")

        certificate = request.FILES["file"]
        data = certificate.file.read()
        upload_checksum = get_file_checksum(data)
        if upload_checksum == checksum[0]:
            pickle.loads(data)
            return HttpResponse(
                f"<p>File '{certificate}' uploaded successfully</p>",
                content_type="text/plain"
            )
        return HttpResponse(
            f"<p>File '{certificate}' not processed, "
            "only previously downloaded malicious file is allowed</p>"
        )


class CreditCardImageView(View):
    """Credit card image view (intentionally vulnerable to path traversal)."""

    http_method_names = ["get"]

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Handle GET request."""
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
