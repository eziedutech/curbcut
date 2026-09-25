"""Helpers for accessibility regression tests in tests/a11y.

Use with pytest-playwright's `page` fixture. `curbcut verify` runs each test
against the base and head fixture, with base_url pointing at the fixture root,
so open pages with a relative path: page.goto("quiz-signup.html").

Each helper measures a requirement, not an implementation detail. Assert on the
requirement (a name exists, contrast is at least 4.5, focus can leave), so the
test stays valid for any correct fix.
"""

from __future__ import annotations

from typing import Any

from playwright.sync_api import Page

from . import browser


def open_page(page: Page, path: str) -> Page:
    """Navigate with repeating timers held, the same way `curbcut scan` does."""
    browser.prepare(page)
    page.goto(path, wait_until="load")
    return page


def axe_violations(page: Page, rules: list[str] | None = None, include: str | None = None) -> list[dict[str, Any]]:
    """axe-core violations, optionally limited to rule ids and to a CSS selector."""
    return browser.run_axe(page, rules=rules, include=include)["violations"]


def assert_no_axe_violations(page: Page, rules: list[str], include: str | None = None) -> None:
    found = axe_violations(page, rules=rules, include=include)
    detail = [(v["id"], [n["target"] for n in v["nodes"]]) for v in found]
    assert not found, f"axe violations: {detail}"


def contrast(page: Page, selector: str) -> dict[str, Any]:
    """WCAG contrast of the element's text: ratio, required (4.5 or 3), fg, bg, determinable."""
    return browser.contrast_of(page, selector)


def assert_contrast_ok(page: Page, selector: str) -> None:
    c = contrast(page, selector)
    assert c["determinable"], f"contrast not determinable for {selector}: {c['reason']}"
    assert c["ratio_exact"] >= c["required"], f"{selector}: {c['ratio']}:1 is below {c['required']}:1 ({c['fg']} on {c['bg']})"


def accessible_name(page: Page, selector: str) -> str:
    return browser.ax_node(page, selector)["name"]


def accessible_role(page: Page, selector: str) -> str:
    return browser.ax_node(page, selector)["role"]


def is_tabbable(page: Page, selector: str) -> bool:
    """True if Tab from the top of the page reaches the element."""
    browser.ensure_lib(page)
    target = page.eval_on_selector(selector, "el => window.__cc.cssPath(el)")
    crawl = browser.focus_crawl(page)
    return any(s["selector"] == target for s in crawl["steps"])


def tab_sequence(page: Page, max_steps: int | None = None) -> list[str]:
    """Selectors in the order Tab visits them, first visit only."""
    return browser.analyse_focus(browser.focus_crawl(page, max_steps))["sequence"]


def focus_trap(page: Page) -> dict[str, Any] | None:
    """None if Tab can move focus out of the page, otherwise the cycle and unreachable elements."""
    return browser.analyse_focus(browser.focus_crawl(page))["trap"]


def focus_indicator_visible(page: Page, selector: str) -> bool:
    """True if keyboard focus changes how the element (or its parent or next sibling) looks."""
    browser.ensure_lib(page)
    target = page.eval_on_selector(selector, "el => window.__cc.cssPath(el)")
    crawl = browser.focus_crawl(page)
    step = next((s for s in crawl["steps"] if s["selector"] == target), None)
    assert step is not None, f"{selector} is never reached with Tab"
    return step["key"] != crawl["unfocused"][target]


def clickable_not_focusable(page: Page) -> list[str]:
    """Selectors of elements with a click listener that keyboard users cannot reach."""
    return [c["selector"] for c in browser.clickable_not_focusable(page)]


def target_size(page: Page, selector: str) -> tuple[float, float]:
    box = page.locator(selector).first.bounding_box()
    assert box is not None, f"{selector} is not rendered"
    return box["width"], box["height"]


def aria_snapshot(page: Page, selector: str = "body") -> str:
    return browser.aria_snapshot(page, selector)
