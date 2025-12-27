"""
Pytest configuration and fixtures for end-to-end tests.

This module provides fixtures and configuration for Playwright-based
end-to-end tests of the insecure banking application.
"""

import pytest
from playwright.sync_api import Page, Browser, BrowserContext


# Override pytest-django fixture to prevent DB setup for e2e tests
@pytest.fixture(scope="session")
def django_db_setup():
    """Override Django DB setup for e2e tests - they use live application."""
    pass


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    """Override Django DB settings modification."""
    pass


# Override the autouse fixture from root conftest to not require DB
@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests():
    """Override root conftest fixture to avoid DB access requirement."""
    pass


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for all e2e tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="function")
def context(browser: Browser):
    """Create a new browser context for each test."""
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext):
    """Create a new page for each test."""
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the application."""
    return "http://localhost:8000"


@pytest.fixture(scope="session")
def test_credentials():
    """Test user credentials."""
    return {
        "username": "john",
        "password": "test"
    }


@pytest.fixture
def logged_in_page(page: Page, base_url: str, test_credentials: dict):
    """Fixture that provides a page with user already logged in."""
    # Navigate to login page
    page.goto(f"{base_url}/login")
    
    # Fill in login form
    page.fill('input[name="username"]', test_credentials["username"])
    page.fill('input[name="password"]', test_credentials["password"])
    
    # Submit login form
    page.click('button[type="submit"], input[type="submit"]')
    
    # Wait for navigation to dashboard
    page.wait_for_url(f"{base_url}/dashboard")
    
    return page
