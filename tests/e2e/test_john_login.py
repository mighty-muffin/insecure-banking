import os
import pytest
from playwright.sync_api import Page, expect
from web.models import Account

# Allow sync DB access in async context
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

@pytest.mark.e2e
def test_john_login(page: Page, live_server):
    username = "john"
    password = "test"

    # Create the Account for John
    # The application logic requires an Account record to exist for authentication to succeed.
    Account.objects.create(
        username=username,
        name="John",
        surname="Doe",
        password=password
    )

    # Go to login page
    page.goto(f"{live_server.url}/login")

    # Fill login form
    page.fill("input[name='username']", username)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")

    # Assert we are redirected to dashboard
    expect(page).to_have_url(f"{live_server.url}/dashboard")

    # Assert dashboard header is visible
    expect(page.locator(".heading h2")).to_contain_text("DASHBOARD")
