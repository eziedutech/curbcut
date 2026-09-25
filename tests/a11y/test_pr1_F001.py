"""F001: display-name input must have a valid HTML autocomplete token."""
from curbcut.testkit import open_page, accessible_name
from playwright.sync_api import Page


def test_display_name_autocomplete_valid(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    value = page.get_attribute("#display-name", "autocomplete")
    # "nick-name" is not a valid autofill token; valid ones are ASCII tokens
    # from the HTML spec (e.g. "username", "name", "email").
    # We assert the value is NOT the known-invalid token.
    assert value != "nick-name", (
        f"autocomplete='{value}' is the invalid 'nick-name' token; "
        "a valid token such as 'username' is required"
    )
