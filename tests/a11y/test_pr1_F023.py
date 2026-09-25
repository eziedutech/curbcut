"""F023: the email input must have a programmatic label (label[for=email])."""
from curbcut.testkit import open_page, assert_no_axe_violations
from playwright.sync_api import Page


def test_email_input_has_programmatic_label(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    # axe's label rule checks that every form control has a programmatic label.
    assert_no_axe_violations(page, rules=["label"], include="#email")
