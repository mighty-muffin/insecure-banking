"""Script to update @patch decorators."""

import re
from pathlib import Path


def update_patches(content: str) -> str:
    """Update @patch decorators."""
    # Update web.services patches
    content = re.sub(r"@patch\('web\.services\.AccountService", r"@patch('apps.accounts.services.AccountService", content)
    content = re.sub(r"@patch\('web\.services\.CashAccountService", r"@patch('apps.banking.services.CashAccountService", content)
    content = re.sub(r"@patch\('web\.services\.CreditAccountService", r"@patch('apps.banking.services.CreditAccountService", content)
    content = re.sub(r"@patch\('web\.services\.ActivityService", r"@patch('apps.banking.services.ActivityService", content)
    content = re.sub(r"@patch\('web\.services\.TransferService", r"@patch('apps.transfers.services.TransferService", content)
    content = re.sub(r"@patch\('web\.services\.StorageService", r"@patch('apps.banking.services.StorageService", content)
    content = re.sub(r"@patch\('web\.services\.connection", r"@patch('apps.banking.services.connection", content)
    content = re.sub(r"@patch\('web\.services\.User", r"@patch('apps.accounts.auth.User", content)

    # Update web.models patches
    content = re.sub(r"@patch\('web\.models\.Account", r"@patch('apps.accounts.models.Account", content)
    content = re.sub(r"@patch\('web\.models\.CashAccount", r"@patch('apps.banking.models.CashAccount", content)
    content = re.sub(r"@patch\('web\.models\.CreditAccount", r"@patch('apps.banking.models.CreditAccount", content)
    content = re.sub(r"@patch\('web\.models\.Transaction", r"@patch('apps.banking.models.Transaction", content)
    content = re.sub(r"@patch\('web\.models\.Transfer", r"@patch('apps.transfers.models.Transfer", content)

    # Update web.views patches
    content = re.sub(r"@patch\('web\.views\.AccountService", r"@patch('apps.accounts.services.AccountService", content)
    content = re.sub(r"@patch\('web\.views\.CashAccountService", r"@patch('apps.banking.services.CashAccountService", content)
    content = re.sub(r"@patch\('web\.views\.CreditAccountService", r"@patch('apps.banking.services.CreditAccountService", content)
    content = re.sub(r"@patch\('web\.views\.ActivityService", r"@patch('apps.banking.services.ActivityService", content)
    content = re.sub(r"@patch\('web\.views\.TransferService", r"@patch('apps.transfers.services.TransferService", content)
    content = re.sub(r"@patch\('web\.views\.storage_service", r"@patch('apps.banking.views.storage_service", content)
    content = re.sub(r"@patch\('web\.views\.checksum", r"@patch('apps.banking.views.checksum", content)
    content = re.sub(r"@patch\('web\.views\.to_traces", r"@patch('apps.banking.views.to_traces", content)

    return content


def main():
    """Main function."""
    base_dir = Path(__file__).parent
    tests_dir = base_dir / "tests"

    updated = 0
    for py_file in tests_dir.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            original = content
            content = update_patches(content)

            if content != original:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated: {py_file}")
                updated += 1
        except Exception as e:
            print(f"Error updating {py_file}: {e}")

    print(f"\nUpdated {updated} files")


if __name__ == "__main__":
    main()
