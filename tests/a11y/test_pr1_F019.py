"""F019: date input must have a visible format hint describing the expected format."""
from curbcut.testkit import open_page
from playwright.sync_api import Page


def test_date_input_format_hint_is_visible(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    # Any visible element near the date field that mentions the expected format.
    hint = page.locator("#quiz-date-hint")
    assert hint.count() > 0, (
        "No #quiz-date-hint element found; format instructions are missing (WCAG 1.3.5 / 3.3.2)"
    )
    assert hint.is_visible(), (
        "#quiz-date-hint exists but is not visible; users cannot see the expected date format"
    )
    hint_text = hint.inner_text().strip()
    assert hint_text, "#quiz-date-hint is visible but has no text"
