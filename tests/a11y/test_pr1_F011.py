"""F011: help-icon buttons must meet the 24x24 px minimum target size (WCAG 2.5.8)."""
from curbcut.testkit import open_page, target_size
from playwright.sync_api import Page

MIN_PX = 24.0


def test_help_about_levels_target_size(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    w, h = target_size(page, "button.help-icon[data-help='help-levels']")
    assert w >= MIN_PX and h >= MIN_PX, (
        f"'Help about levels' button target size is {w}x{h}px; "
        f"minimum required is {MIN_PX}x{MIN_PX}px (WCAG 2.5.8)"
    )
