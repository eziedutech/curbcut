"""F007: the sign-up trigger must be a keyboard-operable native button."""
from curbcut.testkit import open_page, accessible_role
from playwright.sync_api import Page


def test_submit_is_keyboard_operable_button(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    # The element must be reachable by Tab.
    # A native <button> is focusable by default; a plain <div> is not.
    element = page.locator("#submit-signup")
    tag = page.evaluate("el => el.tagName.toLowerCase()", element.element_handle())
    assert tag == "button", (
        f"#submit-signup is a <{tag}> element; it must be a <button> to be keyboard-operable"
    )
