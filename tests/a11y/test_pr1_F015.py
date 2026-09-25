"""F015: date input must expose a visible format hint linked via aria-describedby."""
from curbcut.testkit import open_page
from playwright.sync_api import Page


def test_date_input_has_visible_format_hint(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    described_by = page.get_attribute("#quiz-date", "aria-describedby") or ""
    assert described_by, (
        "#quiz-date has no aria-describedby; the format hint is not programmatically linked"
    )
    # At least one of the referenced elements must be visible and non-empty.
    ids = described_by.split()
    visible_hint_found = False
    for ref_id in ids:
        el = page.locator(f"#{ref_id}")
        if el.count() and el.is_visible():
            text = el.inner_text().strip()
            if text:
                visible_hint_found = True
                break
    assert visible_hint_found, (
        f"aria-describedby references {ids} but none of them is a visible non-empty element"
    )
