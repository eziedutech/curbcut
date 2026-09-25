"""F020: error messages must include a correction example, not just mark the field invalid."""
from curbcut.testkit import open_page
from playwright.sync_api import Page


def test_error_message_includes_correction_example(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    page.locator("#submit-signup").click()

    # The date error message must include enough information to correct the entry.
    date_error = page.locator("#quiz-date-error")
    assert date_error.is_visible(), (
        "Date field error message is not visible after failed submit"
    )
    text = date_error.inner_text().strip().lower()
    assert text, "Date error element has no text content"
    # The message must contain a format reference or example (WCAG 3.3.3).
    assert "dd" in text or "yyyy" in text or "example" in text or "/" in text, (
        f"Date error message '{text}' does not include a correction example or format guidance"
    )
