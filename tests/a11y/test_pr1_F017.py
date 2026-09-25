"""F017: changing the course select must not trigger unexpected navigation."""
from curbcut.testkit import open_page
from playwright.sync_api import Page


def test_course_select_change_does_not_navigate(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    original_url = page.url

    # Select a course value that previously triggered a redirect.
    page.select_option("#course-select", value="maths")

    # Wait a short moment for any synchronous navigation to happen.
    page.wait_for_timeout(300)

    assert page.url == original_url, (
        f"Selecting 'maths' navigated away from {original_url} to {page.url}; "
        "an on-change navigation is an unexpected context change (WCAG 3.2.2)"
    )
