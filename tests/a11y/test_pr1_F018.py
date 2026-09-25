"""F018: validation errors must not be indicated by color alone; text error messages are required."""
from curbcut.testkit import open_page
from playwright.sync_api import Page


def test_validation_error_has_text_not_color_only(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    page.locator("#submit-signup").click()

    # At least one visible, non-empty text error element must be present.
    error_email = page.locator("#email-error")
    assert error_email.is_visible(), (
        "No visible text error message for the email field after failed submit; "
        "error is indicated by color alone (WCAG 1.4.1)"
    )
    assert error_email.inner_text().strip(), (
        "Email error element is visible but has no text content"
    )
