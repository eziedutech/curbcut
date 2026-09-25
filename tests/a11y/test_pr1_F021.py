"""F021: the custom checkbox (#agree) must expose its checked state via aria-checked."""
from curbcut.testkit import open_page
from playwright.sync_api import Page


def test_agree_checkbox_exposes_checked_state(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")

    # Initial state must declare aria-checked (true or false).
    initial = page.get_attribute("#agree", "aria-checked")
    assert initial in {"true", "false"}, (
        f"#agree aria-checked='{initial}' before interaction; "
        "a custom checkbox must expose its state via aria-checked (WCAG 4.1.2)"
    )

    # After clicking, the state must toggle.
    page.locator("#agree").click()
    after = page.get_attribute("#agree", "aria-checked")
    assert after in {"true", "false"}, (
        f"#agree aria-checked='{after}' after click; attribute must remain valid"
    )
    assert after != initial, (
        f"#agree aria-checked did not change after click (was '{initial}', still '{after}')"
    )
