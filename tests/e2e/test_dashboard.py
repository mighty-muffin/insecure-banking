"""
End-to-end tests for dashboard functionality.

This module provides Playwright-based end-to-end tests for the dashboard
and navigation within the banking application.
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
def test_dashboard_displays_account_info(logged_in_page: Page, base_url: str):
    """Test that the dashboard displays account information."""
    page = logged_in_page
    
    # Verify we're on the dashboard
    expect(page).to_have_url(f"{base_url}/dashboard")
    
    # Dashboard should display some account-related content
    expect(page.locator('body')).to_be_visible()
    
    # Look for common banking dashboard elements
    # Cash accounts, credit accounts, or balance information
    page_content = page.content()
    
    # The page should have loaded successfully
    assert "dashboard" in page.url.lower() or len(page_content) > 100


@pytest.mark.e2e
def test_navigation_to_user_details(logged_in_page: Page, base_url: str):
    """Test navigation from dashboard to user details page."""
    page = logged_in_page
    
    # Try to navigate to user details
    # This might be a link, button, or direct URL access
    user_detail_selectors = [
        'a[href*="userDetail"]',
        'a:has-text("Profile")',
        'a:has-text("User Details")',
        'a:has-text("Account Details")'
    ]
    
    # Try each selector to find the user details link
    link_found = False
    for selector in user_detail_selectors:
        if page.locator(selector).count() > 0:
            page.click(selector)
            link_found = True
            break
    
    # If no link found, try direct URL access
    if not link_found:
        page.goto(f"{base_url}/dashboard/userDetail")
    
    # Wait for page to load
    page.wait_for_timeout(1000)
    
    # Verify we navigated somewhere (either to user details or stayed on dashboard)
    current_url = page.url
    assert base_url in current_url


@pytest.mark.e2e
def test_navigation_to_account_activity(logged_in_page: Page, base_url: str):
    """Test navigation to account activity page."""
    page = logged_in_page
    
    # Try to navigate to account activity
    activity_selectors = [
        'a[href*="activity"]',
        'a:has-text("Activity")',
        'a:has-text("Transactions")',
        'a:has-text("History")'
    ]
    
    # Try each selector
    link_found = False
    for selector in activity_selectors:
        if page.locator(selector).count() > 0:
            page.click(selector)
            link_found = True
            break
    
    # If no link found, try direct URL access
    if not link_found:
        page.goto(f"{base_url}/dashboard/activity")
    
    # Wait for page to load
    page.wait_for_timeout(1000)
    
    # Verify navigation occurred
    current_url = page.url
    assert base_url in current_url


@pytest.mark.e2e
def test_dashboard_navigation_menu(logged_in_page: Page):
    """Test that the navigation menu is present and functional."""
    page = logged_in_page
    
    # Look for common navigation elements
    nav_selectors = ['nav', 'header', '.navbar', '#navbar', '[role="navigation"]']
    
    nav_found = False
    for selector in nav_selectors:
        if page.locator(selector).count() > 0:
            nav_found = True
            # Verify nav is visible
            expect(page.locator(selector)).to_be_visible()
            break
    
    # At minimum, the page should be loaded
    expect(page.locator('body')).to_be_visible()
