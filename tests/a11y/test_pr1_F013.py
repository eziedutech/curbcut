"""F013: Tab must visit all focusable elements in the terms section without looping."""
from curbcut.testkit import open_page, focus_trap
from playwright.sync_api import Page


def test_terms_section_not_in_focus_trap(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    trap = focus_trap(page)
    assert trap is None, (
        f"Keyboard focus does not escape the page; elements unreachable: "
        f"{trap['unreachable']}"
    )
