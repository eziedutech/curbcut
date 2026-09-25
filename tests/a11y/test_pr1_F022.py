"""F022: the Close-terms button must have an accessible name."""
from curbcut.testkit import open_page, accessible_name
from playwright.sync_api import Page


def test_close_terms_button_has_accessible_name(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    name = accessible_name(page, "#close-terms")
    assert name.strip(), (
        "The #close-terms button has no accessible name; screen reader users cannot identify "
        "its purpose (WCAG 4.1.2)"
    )
