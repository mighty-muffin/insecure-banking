from playwright.sync_api import Page, expect
from web.models import Account

def login_user(page: Page, live_server_url: str, username: str = "testuser", password: str = "password123"):
    # Ensure user exists (this might fail if called multiple times with same user, so we handle it)
    if not Account.objects.filter(username=username).exists():
        Account.objects.create(
            username=username,
            name="Test",
            surname="User",
            password=password
        )

    page.goto(f"{live_server_url}/login")
    page.fill("input[name='username']", username)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")
    expect(page).to_have_url(f"{live_server_url}/dashboard")
