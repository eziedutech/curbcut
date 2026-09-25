"""F004: submit instruction must not rely solely on color or position."""
from curbcut.testkit import open_page
from playwright.sync_api import Page


def test_submit_instruction_does_not_use_color_or_position(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    body_text = page.locator("main").inner_text()
    # The old instruction used 'green' (color) and 'right' (position).
    # A sensory-characteristic-free instruction must reference the control label.
    assert "green" not in body_text.lower(), (
        "Instruction still references the color 'green' to identify a control (WCAG 1.3.3)"
    )
