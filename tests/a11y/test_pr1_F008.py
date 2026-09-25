"""F008: Tab must not be trapped inside the terms section."""
from curbcut.testkit import open_page, focus_trap
from playwright.sync_api import Page


def test_no_focus_trap_in_terms(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    trap = focus_trap(page)
    assert trap is None, (
        f"Keyboard focus is trapped: cycle={trap['cycle']}, "
        f"unreachable={trap['unreachable']}"
    )
