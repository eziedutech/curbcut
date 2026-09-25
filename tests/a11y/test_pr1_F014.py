"""F014: the 'View course rules' link must have a descriptive accessible name."""
from curbcut.testkit import open_page, accessible_name
from playwright.sync_api import Page

_VAGUE = {"click here", "here", "read more", "more", "link", "this"}


def test_course_rules_link_name_is_descriptive(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    # The rules link points to course.html#rules.
    link = page.locator('a[href="course.html#rules"]').last
    name = accessible_name(page, 'a[href="course.html#rules"]:last-of-type')
    # Fall back to inner_text if ax_node cannot find via :last-of-type.
    if not name:
        name = link.inner_text().strip()
    assert name.lower() not in _VAGUE, (
        f"Link accessible name is '{name}'; vague link text does not describe the destination "
        "(WCAG 2.4.6 / 2.4.9)"
    )
    assert name, "Link has no accessible name"
