"""F005: invalid fields must expose aria-invalid and a visible text error message."""
from curbcut.testkit import open_page
from playwright.sync_api import Page


def test_invalid_field_has_aria_invalid_and_visible_error(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    # Submit the form without filling any field to trigger validation.
    page.locator("#submit-signup").click()

    # The email field must be marked invalid programmatically.
    aria_invalid = page.get_attribute("#email", "aria-invalid")
    assert aria_invalid == "true", (
        f"#email aria-invalid='{aria_invalid}' after failed submit; expected 'true'"
    )

    # A visible text error message must exist (not hidden).
    error = page.locator("#email-error")
    assert error.is_visible(), "Email error message is not visible after failed submit"
    error_text = error.inner_text().strip()
    assert error_text, "Email error message element is visible but contains no text"
