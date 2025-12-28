import os
import pytest
from playwright.sync_api import Page, expect
from web.models import CashAccount
from tests.e2e.utils import login_user

# Allow sync DB access in async context
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

@pytest.mark.e2e
def test_transfer_flow(page: Page, live_server):
    username = "transferuser"
    password = "password123"

    # Login
    login_user(page, live_server.url, username, password)

    # Create a cash account for the user so they can transfer from it
    CashAccount.objects.create(
        number="1001",
        username=username,
        description="Main Account",
        availableBalance=1000.0
    )

    # Create a destination cash account
    CashAccount.objects.create(
        number="9999",
        username="otheruser",
        description="Other Account",
        availableBalance=0.0
    )

    # Navigate to Transfer page
    page.click("text=Transfers")
    page.click("text=Make a transfer")
    expect(page).to_have_url(f"{live_server.url}/transfer")

    # Fill Transfer Form
    # Select the first option in the dropdown (or specific value if we knew it)
    page.select_option("select[name='fromAccount']", value="1001")
    page.fill("input[name='toAccount']", "9999")
    page.fill("input[name='description']", "Test Transfer")
    page.fill("input[name='amount']", "100")

    # Submit
    page.click("button:has-text('Send')")

    # Expect Confirmation Check Page
    expect(page.locator("h4")).to_contain_text("DETAILS CONFIRMATION")
    expect(page.locator("td", has_text="1001")).to_be_visible()
    expect(page.locator("td", has_text="9999")).to_be_visible()
    expect(page.locator("td", has_text="100.0 $")).to_be_visible()

    # Confirm Transfer
    page.click("button[name='action'][value='confirm']")

    # Expect Success Page
    expect(page.locator(".widget-header h3")).to_contain_text("TRANSFER CONFIRMATION")
    expect(page.locator(".alert-success")).to_contain_text("Success! You have successfully made the transfer.")
    expect(page.locator("td", has_text="1001")).to_be_visible()
    expect(page.locator("td", has_text="9999")).to_be_visible()
    expect(page.locator("td", has_text="100.0 $")).to_be_visible()
