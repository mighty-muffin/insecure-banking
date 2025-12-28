import os
import pytest
from playwright.sync_api import Page, expect
from web.models import Account
from tests.e2e.utils import login_user

# Allow sync DB access in async context
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

@pytest.mark.e2e
def test_login_john(page: Page, live_server):
    username = "John"
    password = "test"

    # Create account for John
    Account.objects.create(
        username=username,
        name="John",
        surname="Doe",
        password=password
    )

    # Login
    page.goto(f"{live_server.url}/login")
    page.fill("input[name='username']", username)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")

    # Expect dashboard
    expect(page).to_have_url(f"{live_server.url}/dashboard")
