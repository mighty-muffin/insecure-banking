import os
import pytest
from datetime import datetime
from playwright.sync_api import Page, expect
from web.models import CashAccount, Transaction
from tests.e2e.utils import login_user

# Allow sync DB access in async context
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

@pytest.mark.e2e
def test_activity_view(page: Page, live_server):
    username = "activityuser"
    password = "password123"
    account_number = "2001"

    # Login
    login_user(page, live_server.url, username, password)

    # Create a cash account
    CashAccount.objects.create(
        number=account_number,
        username=username,
        description="Activity Account",
        availableBalance=500.0
    )

    # Create some transactions
    Transaction.objects.create(
        number=account_number,
        description="Deposit",
        amount=500.0,
        availableBalance=500.0,
        date=datetime.now()
    )
    Transaction.objects.create(
        number=account_number,
        description="Payment",
        amount=-50.0,
        availableBalance=450.0,
        date=datetime.now()
    )

    # Navigate to Activity page
    page.click("text=Accounts activity")
    expect(page).to_have_url(f"{live_server.url}/activity")

    # Verify transactions are listed
    # Assuming the table displays description and amount
    expect(page.locator("body")).to_contain_text("Deposit")
    expect(page.locator("body")).to_contain_text("500.0")
    expect(page.locator("body")).to_contain_text("Payment")
    expect(page.locator("body")).to_contain_text("-50.0")
