"""F016: the html element must have a lang attribute so screen readers use the correct voice."""
from curbcut.testkit import open_page
from playwright.sync_api import Page


def test_html_lang_attribute_present(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    lang = page.get_attribute("html", "lang") or ""
    assert lang.strip(), (
        "The <html> element has no lang attribute; screen readers cannot select the correct "
        "language voice (WCAG 3.1.1)"
    )
