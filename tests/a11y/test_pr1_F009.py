"""F009: the page must not auto-refresh or redirect without user control."""
from curbcut.testkit import open_page
from playwright.sync_api import Page


def test_no_meta_refresh(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    refresh_tags = page.locator('meta[http-equiv="refresh"]').count()
    assert refresh_tags == 0, (
        "A meta[http-equiv=refresh] tag exists; the page will redirect without user control "
        "(WCAG 2.2.2 / 3.2.5)"
    )
