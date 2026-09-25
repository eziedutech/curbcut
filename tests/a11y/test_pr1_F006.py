"""F006: keyboard users must be able to dismiss help panels with Escape."""
from curbcut.testkit import open_page
from playwright.sync_api import Page


def test_escape_dismisses_help_panel(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    # Open a help panel via click.
    page.locator("button.help-icon[data-help='help-levels']").click()
    assert page.locator("#help-levels").is_visible(), (
        "Help panel did not open on click; test pre-condition failed"
    )

    # Press Escape: the panel must be dismissed.
    page.keyboard.press("Escape")
    assert not page.locator("#help-levels").is_visible(), (
        "Help panel is still visible after Escape; keyboard users cannot dismiss it"
    )
