"""F002: hint text must meet WCAG 1.4.3 minimum contrast (4.5:1 against white)."""
from curbcut.testkit import open_page, assert_contrast_ok
from playwright.sync_api import Page


def test_hint_text_contrast(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    assert_contrast_ok(page, ".hint")
