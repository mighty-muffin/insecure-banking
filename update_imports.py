"""Script to update imports from old structure to new structure."""

import os
import re
from pathlib import Path


def update_imports(content: str) -> str:
    """Update imports in content."""
    # Model imports
    content = re.sub(
        r'from web\.models import.*',
        lambda m: convert_model_import(m.group(0)),
        content
    )

    # Service imports - need to be more specific
    content = re.sub(
        r'from web\.services import\s+([\w\s,]+)',
        lambda m: convert_service_import(m.group(0), m.group(1)),
        content
    )

    # View imports
    content = re.sub(
        r'from web\.views import\s+([\w\s,]+)',
        lambda m: convert_view_import(m.group(0), m.group(1)),
        content
    )

    # Context processor imports
    content = content.replace(
        'from web.context_processors import',
        'from apps.core.context_processors import'
    )

    # Data imports
    content = content.replace('from data.', 'from apps.core.')

    return content


def convert_model_import(import_line: str) -> str:
    """Convert model imports to new structure."""
    # Extract imported names
    match = re.search(r'import\s+(.*)', import_line)
    if not match:
        return import_line

    names = [n.strip() for n in match.group(1).split(',')]

    imports = []
    if 'Account' in names:
        imports.append('from apps.accounts.models import Account')

    banking_models = [n for n in names if n in ['CashAccount', 'CreditAccount', 'Transaction']]
    if banking_models:
        imports.append(f'from apps.banking.models import {", ".join(banking_models)}')

    if 'Transfer' in names or 'ModelSerializationMixin' in names:
        transfer_imports = [n for n in names if n in ['Transfer', 'ModelSerializationMixin']]
        imports.append(f'from apps.transfers.models import {", ".join(transfer_imports)}')

    return '\n'.join(imports) if imports else import_line


def convert_service_import(import_line: str, names_str: str) -> str:
    """Convert service imports to new structure."""
    names = [n.strip() for n in names_str.split(',')]

    imports = []
    if 'AccountService' in names:
        imports.append('from apps.accounts.services import AccountService')

    banking_services = [n for n in names if n in ['CashAccountService', 'CreditAccountService', 'ActivityService', 'StorageService']]
    if banking_services:
        imports.append(f'from apps.banking.services import {", ".join(banking_services)}')

    if 'TransferService' in names:
        imports.append('from apps.transfers.services import TransferService')

    return '\n'.join(imports) if imports else import_line


def convert_view_import(import_line: str, names_str: str) -> str:
    """Convert view imports to new structure."""
    names = [n.strip() for n in names_str.split(',')]

    imports = []

    # Determine what goes where
    banking_items = []
    transfer_items = []

    for name in names:
        if name in ['Trusted', 'Untrusted', 'get_file_checksum', 'to_traces', 'checksum',
                    'StorageService', 'secretKey', 'resources']:
            banking_items.append(name)
        elif name in ['TransferView', 'TransferForm']:
            transfer_items.append(name)
        else:
            # Default to banking for views
            banking_items.append(name)

    if banking_items:
        imports.append(f'from apps.banking.views import {", ".join(banking_items)}')
    if transfer_items:
        imports.append(f'from apps.transfers.views import {", ".join(transfer_items)}')

    return '\n'.join(imports) if imports else import_line


def update_file(filepath: Path):
    """Update imports in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content
        content = update_imports(content)

        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"Error updating {filepath}: {e}")
        return False


def main():
    """Main function."""
    base_dir = Path(__file__).parent
    tests_dir = base_dir / "tests"

    updated = 0
    for py_file in tests_dir.rglob("*.py"):
        if update_file(py_file):
            updated += 1

    print(f"\nUpdated {updated} files")


if __name__ == "__main__":
    main()
