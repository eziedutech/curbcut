"""Measurements taken in a real Chromium page.

Shared by `curbcut scan` and by `curbcut.testkit`, so a regression test and the
scan that produced the fact use the same code path.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from playwright.sync_api import Page

AXE_PATH = Path(__file__).parent / "vendor" / "axe.min.js"

# Tags that map to WCAG 2.2 Level A and AA, plus axe best practices.
AXE_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"]

# Repeating timers (carousels, tickers) are held so two scans see the same state.
# setTimeout is left alone because axe-core itself depends on it.
_HOLD_INTERVALS = """
(() => {
  window.__ccHeldIntervals = 0;
  window.setInterval = function () { window.__ccHeldIntervals += 1; return 0; };
})();
"""

_LIB = r"""
() => {
  if (window.__cc) return;
  const FOCUSABLE = 'a[href],area[href],button,input,select,textarea,iframe,summary,[tabindex],[contenteditable=""],[contenteditable="true"],audio[controls],video[controls]';

  function uniqueId(el) {
    return el.id && document.querySelectorAll('#' + CSS.escape(el.id)).length === 1;
  }
  function cssPath(el) {
    if (!(el instanceof Element)) return null;
    const parts = [];
    while (el && el.nodeType === 1 && el !== document.documentElement) {
      if (uniqueId(el)) { parts.unshift('#' + CSS.escape(el.id)); return parts.join(' > '); }
      let part = el.localName;
      const parent = el.parentElement;
      if (parent) {
        const same = Array.from(parent.children).filter(c => c.localName === el.localName);
        if (same.length > 1) part += ':nth-of-type(' + (same.indexOf(el) + 1) + ')';
      }
      parts.unshift(part);
      el = parent;
    }
    return parts.join(' > ');
  }
  function isVisible(el) {
    if (!el.checkVisibility({ checkVisibilityCSS: true })) return false;
    return el.getClientRects().length > 0;
  }
  function isVisuallyHidden(el) {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return (r.width <= 1 && r.height <= 1) || s.clip === 'rect(0px, 0px, 0px, 0px)';
  }
  function tabbables() {
    const all = Array.from(document.querySelectorAll(FOCUSABLE)).filter(el =>
      !el.disabled && el.tabIndex >= 0 && !(el.localName === 'input' && el.type === 'hidden') &&
      !el.closest('[inert]') && isVisible(el));
    // Only one radio per named group takes part in sequential navigation.
    const seenGroups = new Set();
    const dom = [];
    for (const el of all) {
      if (el.localName === 'input' && el.type === 'radio' && el.name) {
        const key = (el.form ? cssPath(el.form) : '') + '|' + el.name;
        if (seenGroups.has(key)) continue;
        seenGroups.add(key);
        const group = all.filter(o => o.localName === 'input' && o.type === 'radio' && o.name === el.name && o.form === el.form);
        dom.push(group.find(o => o.checked) || el);
        continue;
      }
      dom.push(el);
    }
    const positive = dom.filter(e => e.tabIndex > 0).sort((a, b) => a.tabIndex - b.tabIndex);
    return { dom, order: positive.concat(dom.filter(e => e.tabIndex === 0)) };
  }
  function styleKey(el) {
    if (!el) return '';
    const s = getComputedStyle(el);
    // An outline that is not drawn cannot be an indicator, whatever its other values.
    const outline = (s.outlineStyle === 'none' || parseFloat(s.outlineWidth) === 0) ? 'none'
      : [s.outlineStyle, s.outlineWidth, s.outlineColor, s.outlineOffset].join(' ');
    return [outline, s.boxShadow,
      s.borderTopColor, s.borderRightColor, s.borderBottomColor, s.borderLeftColor,
      s.borderTopWidth, s.borderBottomWidth, s.backgroundColor, s.color, s.textDecorationLine].join('|');
  }
  function focusKey(el) {
    // The indicator may be drawn on the element, its parent, or the next sibling (input:focus + label).
    return [styleKey(el), styleKey(el.parentElement), styleKey(el.nextElementSibling)].join('#');
  }
  function parseColor(c) {
    const m = /^rgba?\(([^)]+)\)$/.exec(c.trim());
    if (!m) return null;
    const p = m[1].split(/[\s,\/]+/).filter(Boolean).map(Number);
    if (p.length < 3 || p.some(Number.isNaN)) return null;
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  }
  function blend(top, bottom) {
    const a = top.a;
    return { r: top.r * a + bottom.r * (1 - a), g: top.g * a + bottom.g * (1 - a), b: top.b * a + bottom.b * (1 - a), a: 1 };
  }
  function channel(v) {
    v = v / 255;
    return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  }
  function luminance(c) {
    return 0.2126 * channel(c.r) + 0.7152 * channel(c.g) + 0.0722 * channel(c.b);
  }
  function hex(c) {
    const h = v => Math.round(v).toString(16).padStart(2, '0');
    return '#' + h(c.r) + h(c.g) + h(c.b);
  }
  function contrastOf(el) {
    const s = getComputedStyle(el);
    const out = { selector: cssPath(el), determinable: true, reason: null };
    const layers = [];
    let node = el;
    while (node && node.nodeType === 1) {
      const ns = getComputedStyle(node);
      if (parseFloat(ns.opacity) < 1) { out.determinable = false; out.reason = 'opacity below 1 on ' + cssPath(node); }
      if (ns.backgroundImage !== 'none') { out.determinable = false; out.reason = 'background image on ' + cssPath(node); break; }
      const bg = parseColor(ns.backgroundColor);
      if (bg === null) { out.determinable = false; out.reason = 'unparsed background colour ' + ns.backgroundColor; break; }
      if (bg.a > 0) layers.push(bg);
      if (bg.a === 1) break;
      node = node.parentElement;
    }
    let bg = { r: 255, g: 255, b: 255, a: 1 };
    for (let i = layers.length - 1; i >= 0; i--) bg = blend(layers[i], bg);
    let fg = parseColor(s.color);
    if (fg === null) { out.determinable = false; out.reason = 'unparsed text colour ' + s.color; fg = { r: 0, g: 0, b: 0, a: 1 }; }
    if (fg.a < 1) fg = blend(fg, bg);
    const l1 = luminance(fg), l2 = luminance(bg);
    const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    const size = parseFloat(s.fontSize);
    const bold = parseInt(s.fontWeight, 10) >= 700;
    const large = size >= 24 || (bold && size >= 18.66);
    out.ratio = Math.floor(ratio * 100) / 100;
    out.ratio_exact = ratio;
    out.required = large ? 3 : 4.5;
    out.fg = hex(fg);
    out.bg = hex(bg);
    out.font_size_px = size;
    out.bold = bold;
    out.large_text = large;
    out.text = (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 80);
    return out;
  }
  function textElements() {
    const skip = new Set(['script', 'style', 'noscript', 'title', 'option', 'template']);
    return Array.from(document.body.querySelectorAll('*')).filter(el => {
      if (skip.has(el.localName)) return false;
      if (!Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim().length > 0)) return false;
      if (el.closest(':disabled')) return false;
      return isVisible(el) && !isVisuallyHidden(el);
    });
  }
  window.__cc = { cssPath, isVisible, tabbables, focusKey, contrastOf, textElements };
}
"""


def ensure_lib(page: Page) -> None:
    page.evaluate(_LIB)


def prepare(page: Page) -> None:
    """Hold repeating timers before navigation so repeated scans see the same page."""
    page.add_init_script(_HOLD_INTERVALS)


def run_axe(page: Page, rules: list[str] | None = None, include: str | None = None) -> dict[str, Any]:
    if not page.evaluate("() => typeof window.axe !== 'undefined'"):
        page.add_script_tag(path=str(AXE_PATH))
    options: dict[str, Any] = {"resultTypes": ["violations", "incomplete"]}
    if rules:
        options["runOnly"] = {"type": "rule", "values": rules}
    else:
        options["runOnly"] = {"type": "tag", "values": AXE_TAGS}
        # target-size (WCAG 2.5.8) ships disabled in axe-core 4.13.0; CurbCut turns it on.
        options["rules"] = {"target-size": {"enabled": True}}
    return page.evaluate(
        "async ([ctx, opts]) => { const r = await axe.run(ctx || document, opts);"
        " const slim = list => list.map(v => ({id: v.id, impact: v.impact, tags: v.tags, help: v.help, helpUrl: v.helpUrl,"
        " nodes: v.nodes.map(n => ({target: n.target, html: n.html, impact: n.impact, summary: n.failureSummary || ''}))}));"
        " return {violations: slim(r.violations), incomplete: slim(r.incomplete)}; }",
        [include, options],
    )


def axe_rule_metadata(page: Page) -> list[dict[str, Any]]:
    """Official rule metadata from the vendored axe-core build."""
    if not page.evaluate("() => typeof window.axe !== 'undefined'"):
        page.add_script_tag(path=str(AXE_PATH))
    return page.evaluate(
        "() => axe.getRules().map(r => ({ruleId: r.ruleId, tags: r.tags, help: r.help,"
        " enabled: (axe._audit.rules.find(x => x.id === r.ruleId) || {}).enabled !== false}))"
    )


def contrast_measurements(page: Page) -> list[dict[str, Any]]:
    ensure_lib(page)
    return page.evaluate("() => window.__cc.textElements().map(el => window.__cc.contrastOf(el))")


def contrast_of(page: Page, selector: str) -> dict[str, Any]:
    ensure_lib(page)
    return page.evaluate(
        "sel => { const el = document.querySelector(sel); if (!el) throw new Error('No element for ' + sel);"
        " return window.__cc.contrastOf(el); }",
        selector,
    )


def tabbables(page: Page) -> dict[str, Any]:
    ensure_lib(page)
    return page.evaluate(
        "() => { const t = window.__cc.tabbables(); const d = el => ({selector: window.__cc.cssPath(el),"
        " tabindex: el.tabIndex, key: window.__cc.focusKey(el)});"
        " return {dom: t.dom.map(d), order: t.order.map(d)}; }"
    )


def _active(page: Page) -> dict[str, Any] | None:
    return page.evaluate(
        "() => { const el = document.activeElement;"
        " if (!el || el === document.body || el === document.documentElement) return null;"
        " return {selector: window.__cc.cssPath(el), tag: el.localName, key: window.__cc.focusKey(el)}; }"
    )


def focus_crawl(page: Page, max_steps: int | None = None) -> dict[str, Any]:
    """Press Tab from the top of the page and record where focus goes.

    Returns the tabbable elements in DOM order, the focus sequence, whether focus
    ever left the document, and the focused and unfocused style keys per element.
    """
    ensure_lib(page)
    page.evaluate("() => { if (document.activeElement) document.activeElement.blur(); window.scrollTo(0, 0); }")
    info = tabbables(page)
    unfocused = {t["selector"]: t["key"] for t in info["dom"]}
    limit = max_steps if max_steps is not None else 3 * len(info["dom"]) + 10
    steps: list[dict[str, Any]] = []
    left_document = False
    for _ in range(limit):
        page.keyboard.press("Tab")
        active = _active(page)
        if active is None:
            left_document = True
            break
        steps.append(active)
    return {"dom": info["dom"], "expected_order": info["order"], "steps": steps,
            "left_document": left_document, "unfocused": unfocused}


def analyse_focus(crawl: dict[str, Any]) -> dict[str, Any]:
    """Pure analysis of a focus crawl: traps, positive tabindex, missing indicators."""
    dom_selectors = [t["selector"] for t in crawl["dom"]]
    visited: list[str] = []
    for s in crawl["steps"]:
        if s["selector"] not in visited:
            visited.append(s["selector"])
    trap = None
    if not crawl["left_document"] and crawl["steps"]:
        tail = crawl["steps"][len(crawl["steps"]) * 2 // 3:]
        cycle: list[str] = []
        for s in tail:
            if s["selector"] not in cycle:
                cycle.append(s["selector"])
        cycle.sort(key=visited.index)
        trap = {"cycle": cycle, "unreachable": [s for s in dom_selectors if s not in visited]}
    positive = [
        {"selector": t["selector"], "tabindex": t["tabindex"],
         "dom_position": dom_selectors.index(t["selector"]) + 1,
         "focus_position": (visited.index(t["selector"]) + 1) if t["selector"] in visited else None}
        for t in crawl["dom"] if t["tabindex"] > 0
    ]
    not_visible = []
    not_measured = []
    seen: set[str] = set()
    for s in crawl["steps"]:
        sel = s["selector"]
        if sel in seen or sel not in crawl["unfocused"]:
            continue
        seen.add(sel)
        if s["tag"] == "iframe":
            # The indicator is drawn inside the frame's own document, which this check cannot see.
            not_measured.append({"selector": sel, "reason": "focus moved into an iframe; its indicator is not measured"})
        elif s["key"] == crawl["unfocused"][sel]:
            not_visible.append(sel)
    return {"sequence": visited, "trap": trap, "positive_tabindex": positive,
            "focus_not_visible": not_visible, "focus_not_measured": not_measured}


def clickable_not_focusable(page: Page) -> list[dict[str, Any]]:
    """Elements with a click or pointer listener that keyboard users cannot reach."""
    ensure_lib(page)
    cdp = page.context.new_cdp_session(page)
    try:
        arr = cdp.send("Runtime.evaluate", {"expression": "Array.from(document.body.querySelectorAll('*'))"})
        props = cdp.send("Runtime.getProperties", {"objectId": arr["result"]["objectId"], "ownProperties": True})
        found = []
        for prop in props["result"]:
            if not prop["name"].isdigit():
                continue
            oid = prop["value"]["objectId"]
            listeners = cdp.send("DOMDebugger.getEventListeners", {"objectId": oid})["listeners"]
            types = sorted({ls["type"] for ls in listeners} & {"click", "mousedown", "mouseup", "pointerdown", "pointerup"})
            if not types:
                continue
            desc = cdp.send("Runtime.callFunctionOn", {
                "objectId": oid, "returnByValue": True,
                "functionDeclaration": (
                    "function () { const t = window.__cc.tabbables().dom; const native = this.matches("
                    "'a[href],button,input,select,textarea,summary,label,iframe');"
                    " return {selector: window.__cc.cssPath(this), tag: this.localName, role: this.getAttribute('role'),"
                    " tabbable: t.includes(this) || this.tabIndex >= 0, native, visible: window.__cc.isVisible(this),"
                    " html: this.outerHTML.slice(0, 200)}; }"),
            })["result"]["value"]
            if desc["visible"] and not desc["tabbable"] and not desc["native"]:
                desc["listeners"] = types
                found.append(desc)
        return found
    finally:
        cdp.detach()


def ax_node(page: Page, selector: str) -> dict[str, Any]:
    """Accessible name and role from Chromium's accessibility tree."""
    cdp = page.context.new_cdp_session(page)
    try:
        res = cdp.send("Runtime.evaluate", {"expression": f"document.querySelector({selector!r})"})
        if res["result"].get("subtype") == "null" or "objectId" not in res["result"]:
            raise AssertionError(f"No element matches {selector}")
        node = cdp.send("DOM.describeNode", {"objectId": res["result"]["objectId"]})["node"]
        tree = cdp.send("Accessibility.getPartialAXTree", {"backendNodeId": node["backendNodeId"], "fetchRelatives": False})
        ax = tree["nodes"][0] if tree["nodes"] else {}
        return {
            "name": (ax.get("name") or {}).get("value", ""),
            "role": (ax.get("role") or {}).get("value", ""),
            "ignored": ax.get("ignored", False),
        }
    finally:
        cdp.detach()


def aria_snapshot(page: Page, selector: str = "body") -> str:
    return page.locator(selector).aria_snapshot()
