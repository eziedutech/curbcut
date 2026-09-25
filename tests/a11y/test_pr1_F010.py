"""F010: level radio buttons must show a visible focus indicator when focused by keyboard."""
from curbcut.testkit import open_page, focus_indicator_visible
from playwright.sync_api import Page


def test_level_radio_focus_indicator_visible(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    visible = focus_indicator_visible(page, ".level-radio")
    assert visible, (
        "Keyboard focus on .level-radio does not produce a visible focus indicator (WCAG 2.4.7)"
    )
