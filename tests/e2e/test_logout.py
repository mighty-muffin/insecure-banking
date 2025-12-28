import os
import pytest
from playwright.sync_api import Page, expect
from tests.e2e.utils import login_user

# Allow sync DB access in async context
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

@pytest.mark.e2e
def test_logout(page: Page, live_server):
    username = "logoutuser"
    password = "password123"

    # Login
    login_user(page, live_server.url, username, password)

    # Click Logout
    # Logout is in a dropdown menu under the user's name
    page.click(".logged-user .dropdown-toggle")
    page.click("text=Logout")

    # Expect redirect to login page
    expect(page).to_have_url(f"{live_server.url}/login")
