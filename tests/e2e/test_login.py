import os
import pytest
from playwright.sync_api import Page, expect
from web.models import Account

# Allow sync DB access in async context (if any)
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

@pytest.mark.e2e
def test_login_success(page: Page, live_server):
    # Create a user account
    username = "testuser"
    password = "password123"
    Account.objects.create(
        username=username,
        name="Test",
        surname="User",
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
    expect(page.locator("h2")).to_contain_text("DASHBOARD")

@pytest.mark.e2e
def test_john_login(page: Page, live_server):
    username = "john"
    password = "test"

    # Create the Account for John
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
