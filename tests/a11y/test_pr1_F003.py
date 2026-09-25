"""F003: badge image must have a meaningful (non-generic) accessible name."""
from curbcut.testkit import open_page, accessible_name
from playwright.sync_api import Page


def test_badge_image_meaningful_alt(page: Page, base_url: str) -> None:
    open_page(page, "quiz-signup.html")
    name = accessible_name(page, ".quiz-badge img")
    assert name, "badge image has no accessible name"
    assert name.lower() not in {"image", "img", "photo", "picture", "graphic"}, (
        f"badge image accessible name is the generic word '{name}'; "
        "it must describe the image content"
    )
