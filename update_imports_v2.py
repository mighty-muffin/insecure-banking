"""Script to carefully update imports."""

import os
import re
from pathlib import Path


REPLACEMENTS = [
    # Model imports - specific first
    (r'from web\.models import Account\b', 'from apps.accounts.models import Account'),
    (r'from web\.models import CashAccount\b', 'from apps.banking.models import CashAccount'),
    (r'from web\.models import CreditAccount\b', 'from apps.banking.models import CreditAccount'),
    (r'from web\.models import Transaction\b', 'from apps.banking.models import Transaction'),
    (r'from web\.models import Transfer\b', 'from apps.transfers.models import Transfer'),
    (r'from web\.models import ModelSerializationMixin\b', 'from apps.transfers.models import ModelSerializationMixin'),

    # Multi-import patterns
    (r'from web\.models import ([^(\n]+)', lambda m: convert_multi_model_import(m.group(1))),

    # Service imports
    (r'from web\.services import AccountService\b', 'from apps.accounts.services import AccountService'),
    (r'from web\.services import CashAccountService\b', 'from apps.banking.services import CashAccountService'),
    (r'from web\.services import CreditAccountService\b', 'from apps.banking.services import CreditAccountService'),
    (r'from web\.services import ActivityService\b', 'from apps.banking.services import ActivityService'),
    (r'from web\.services import StorageService\b', 'from apps.banking.services import StorageService'),
    (r'from web\.services import TransferService\b', 'from apps.transfers.services import TransferService'),

    # Multi-import service patterns
    (r'from web\.services import ([^(\n]+)', lambda m: convert_multi_service_import(m.group(1))),

    # View imports
    (r'from web\.views import ([^(\n]+)', lambda m: convert_multi_view_import(m.group(1))),

    # Context processors
    (r'from web\.context_processors import', 'from apps.core.context_processors import'),

    # Patch decorators
    (r"@patch\('web\.services\.AccountService", r"@patch('apps.accounts.services.AccountService"),
    (r"@patch\('web\.services\.CashAccountService", r"@patch('apps.banking.services.CashAccountService"),
    (r"@patch\('web\.services\.CreditAccountService", r"@patch('apps.banking.services.CreditAccountService"),
    (r"@patch\('web\.services\.ActivityService", r"@patch('apps.banking.services.ActivityService"),
    (r"@patch\('web\.services\.TransferService", r"@patch('apps.transfers.services.TransferService"),
    (r"@patch\('web\.services\.StorageService", r"@patch('apps.banking.services.StorageService"),
    (r"@patch\('web\.services\.connection", r"@patch('apps.banking.services.connection"),
    (r"@patch\('web\.services\.User", r"@patch('apps.accounts.auth.User"),
    (r"@patch\('web\.models\.Account", r"@patch('apps.accounts.models.Account"),
    (r"@patch\('web\.models\.CashAccount", r"@patch('apps.banking.models.CashAccount"),
    (r"@patch\('web\.models\.CreditAccount", r"@patch('apps.banking.models.CreditAccount"),
    (r"@patch\('web\.models\.Transaction", r"@patch('apps.banking.models.Transaction"),
    (r"@patch\('web\.models\.Transfer", r"@patch('apps.transfers.models.Transfer"),
    (r"@patch\('web\.views\.AccountService", r"@patch('apps.accounts.services.AccountService"),
    (r"@patch\('web\.views\.CashAccountService", r"@patch('apps.banking.services.CashAccountService"),
    (r"@patch\('web\.views\.CreditAccountService", r"@patch('apps.banking.services.CreditAccountService"),
    (r"@patch\('web\.views\.ActivityService", r"@patch('apps.banking.services.ActivityService"),
    (r"@patch\('web\.views\.TransferService", r"@patch('apps.transfers.services.TransferService"),
    (r"@patch\('web\.views\.storage_service", r"@patch('apps.banking.views.storage_service"),
    (r"@patch\('web\.views\.checksum", r"@patch('apps.banking.views.checksum"),
    (r"@patch\('web\.views\.to_traces", r"@patch('apps.banking.views.to_traces"),
]


def convert_multi_model_import(imports_str):
    """Convert multi-model imports."""
    imports = [i.strip() for i in imports_str.split(',')]
    result = []

    accounts_models = [i for i in imports if i in ['Account']]
    banking_models = [i for i in imports if i in ['CashAccount', 'CreditAccount', 'Transaction']]
    transfer_models = [i for i in imports if i in ['Transfer', 'ModelSerializationMixin']]

    if accounts_models:
        result.append(f"from apps.accounts.models import {', '.join(accounts_models)}")
    if banking_models:
        result.append(f"from apps.banking.models import {', '.join(banking_models)}")
    if transfer_models:
        result.append(f"from apps.transfers.models import {', '.join(transfer_models)}")

    return '\n'.join(result) if result else f"from web.models import {imports_str}"


def convert_multi_service_import(imports_str):
    """Convert multi-service imports."""
    # Handle parenthesized imports
    if '(' in imports_str:
        return f"from web.services import {imports_str}"  # Skip complex multi-line imports

    imports = [i.strip() for i in imports_str.split(',')]
    result = []

    accounts_services = [i for i in imports if i in ['AccountService']]
    banking_services = [i for i in imports if i in ['CashAccountService', 'CreditAccountService', 'ActivityService', 'StorageService']]
    transfer_services = [i for i in imports if i in ['TransferService']]

    if accounts_services:
        result.append(f"from apps.accounts.services import {', '.join(accounts_services)}")
    if banking_services:
        result.append(f"from apps.banking.services import {', '.join(banking_services)}")
    if transfer_services:
        result.append(f"from apps.transfers.services import {', '.join(transfer_services)}")

    return '\n'.join(result) if result else f"from web.services import {imports_str}"


def convert_multi_view_import(imports_str):
    """Convert multi-view imports."""
    # Handle parenthesized imports
    if '(' in imports_str:
        return f"from web.views import {imports_str}"  # Skip complex multi-line imports

    imports = [i.strip() for i in imports_str.split(',')]
    result = []

    accounts_views = [i for i in imports if i in ['LoginView', 'LogoutView', 'AdminView']]
    banking_views = [i for i in imports if i in [
        'ActivityView', 'ActivityCreditView', 'DashboardView', 'UserDetailView',
        'AvatarView', 'AvatarUpdateView', 'CertificateDownloadView',
        'MaliciousCertificateDownloadView', 'NewCertificateView', 'CreditCardImageView',
        'Trusted', 'Untrusted', 'get_file_checksum', 'to_traces', 'StorageService',
        'secretKey', 'resources', 'checksum'
    ]]
    transfer_views = [i for i in imports if i in ['TransferView', 'TransferForm', 'to_traces']]

    if accounts_views:
        result.append(f"from apps.accounts.views import {', '.join(accounts_views)}")
    if banking_views:
        result.append(f"from apps.banking.views import {', '.join(banking_views)}")
    if transfer_views:
        result.append(f"from apps.transfers.views import {', '.join(transfer_views)}")

    return '\n'.join(result) if result else f"from web.views import {imports_str}"


def update_file(filepath):
    """Update a single file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        original = content

        for pattern, replacement in REPLACEMENTS:
            if callable(replacement):
                content = re.sub(pattern, replacement, content)
            else:
                content = re.sub(pattern, replacement, content)

        if content != original:
            with open(filepath, 'w') as f:
                f.write(content)
            return True
    except Exception as e:
        print(f"Error in {filepath}: {e}")
    return False


def main():
    """Main function."""
    base = Path(__file__).parent / "tests"
    updated = 0

    for pyfile in base.rglob("*.py"):
        if update_file(pyfile):
            print(f"Updated: {pyfile}")
            updated += 1

    print(f"\nUpdated {updated} files")


if __name__ == "__main__":
    main()
