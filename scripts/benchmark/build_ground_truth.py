"""Writes ground-truth.json: the planted issues and decoys in the OpenClass fixture.

Kept as code so the list is reviewable and the counts are computed, not typed.
IBM Bob must not read this folder during a review (.bobignore).
"""

import json
from pathlib import Path

P = {"1": "perceivable", "2": "operable", "3": "understandable", "4": "robust"}
Q, L = "quiz-signup.html", "lesson-media.html"


def issue(gt, sc, page, selector, desc, signal, fixable=True, also=()):
    return {
        "gt_id": gt, "sc": sc, "also_accept_sc": list(also), "principle": P[sc[0]], "page": page,
        "selector": selector, "description": desc, "engine_signal": signal,
        "expected_tier": "proven" if signal else "flagged", "fixable": fixable,
    }


def decoy(gt, page, selector, looks_like, why):
    return {"gt_id": gt, "page": page, "selector": selector, "looks_like_sc": looks_like, "why_correct": why}


PR1 = [
    issue("P1-01", "3.1.1", Q, "html", "The page has no lang attribute, so screen readers may read it with the wrong voice.", "axe:html-has-lang"),
    issue("P1-02", "2.2.1", Q, 'meta[http-equiv="refresh"]', "The page redirects to the course page after 300 seconds with no warning or way to extend.", "axe:meta-refresh"),
    issue("P1-03", "4.1.2", Q, "#email", "The email field has a visible word next to it but no programmatic label.", "axe:label", also=["1.3.1", "3.3.2"]),
    issue("P1-04", "1.4.3", Q, ".hint", "Hint text is #9a9a9a on white, a contrast ratio of 2.81:1.", "axe:color-contrast"),
    issue("P1-05", "4.1.2", Q, "#close-terms", "The close button contains only an icon and has no accessible name.", "axe:button-name"),
    issue("P1-06", "4.1.2", Q, "#agree", "The custom checkbox has role checkbox but no aria-checked state.", "axe:aria-required-attr"),
    issue("P1-07", "1.3.5", Q, "#display-name", "The autocomplete value nick-name is not a valid token.", "axe:autocomplete-valid"),
    issue("P1-08", "2.1.2", Q, "#terms-box, #terms-first, #terms-last", "Tab and Shift+Tab loop between the two links in the terms box; keyboard users cannot leave it.", "engine:focus_trap"),
    issue("P1-09", "2.4.7", Q, ".level-radio", "The custom level radios remove the outline on focus and show no other indicator.", "engine:focus_not_visible"),
    issue("P1-10", "2.1.1", Q, "#submit-signup", "The Sign up control is a div with a click handler; it cannot be reached or activated with a keyboard.", "engine:clickable_not_focusable", also=["4.1.2"]),
    issue("P1-11", "1.3.1", Q, ".quiz-options", "The level radios have no fieldset and legend, so the question Choose your level is not tied to them.", None),
    issue("P1-12", "3.3.1", Q, "#email", "Invalid fields only turn red; there is no text describing the error.", None, also=["1.4.1"]),
    issue("P1-13", "1.1.1", Q, ".quiz-badge img", 'The badge image has alt="image", which says nothing about the badge.', None),
    issue("P1-14", "2.4.4", Q, '#signup-form a[href="course.html#rules"]', 'A link reads only "Click here", in its own paragraph, with no programmatic context.', None),
    issue("P1-15", "1.3.3", Q, "#signup-form > p:nth-of-type(3)", "The instruction refers to the green button on the right, relying on colour and position.", None, also=["1.4.1"]),
    issue("P1-16", "2.5.8", Q, ".help-icon", "Two 16 by 16 px help buttons sit next to each other with no spacing.", "axe:target-size"),
    issue("P1-17", "3.3.2", Q, "#quiz-date", "The date field requires DD/MM/YYYY but does not say so.", None),
    issue("P1-18", "3.2.2", Q, "#course-select", "Choosing another course in the select immediately navigates away from the form.", None),
]
PR1_DECOYS = [
    decoy("D1-01", Q, ".help-text", "1.4.3", "Grey text #595959 on white is 7.0:1, above 4.5:1."),
    decoy("D1-02", Q, ".flourish", "1.1.1", 'Purely decorative image with alt="".'),
    decoy("D1-03", Q, "#course-code", "3.3.2", "The label is visually hidden but present and associated; the field is read-only and prefilled."),
    decoy("D1-04", Q, "#course-select", "2.4.7", "The outline is removed but replaced with a 3 px box-shadow focus ring."),
    decoy("D1-05", Q, "#form-status", "4.1.3", "A polite live region used correctly for the status message."),
    decoy("D1-06", Q, "#page-title", "2.4.3", 'tabindex="-1" on the heading only allows programmatic focus; it adds nothing to the tab order.'),
]
PR2 = [
    issue("P2-01", "1.1.1", L, 'img[src="img/leaf.svg"]', "The leaf image has no alt attribute at all.", "axe:image-alt"),
    issue("P2-02", "1.1.1", L, 'img[src="img/stages-chart.svg"]', 'An image of text describing the two stages has alt="chart"; its text is not available.', None, also=["1.4.5"]),
    issue("P2-03", "1.2.2", L, 'video[src="media/intro.webm"]', "Video 1 has no captions track.", None),
    issue("P2-04", "1.4.2", L, "audio", "Background audio starts automatically, loops, and has no control to stop it.", None),
    issue("P2-05", "1.3.1", L, ".data-table:not(:has(caption))", "The growth data table uses td for its header row; no header cells or scope.", None),
    issue("P2-06", "2.2.2", L, "#facts-carousel", "The facts carousel advances every 3 seconds with no pause control.", None),
    issue("P2-07", "4.1.2", L, "iframe", "The practice iframe has no title.", "axe:frame-title"),
    issue("P2-08", "2.4.4", L, '.further a[href="lesson.html"], .further a[href="course.html"]', 'Two links read only "More" and go to different places.', None),
    issue("P2-09", "1.4.3", L, ".figure-caption", "White caption text on #7fb3d5 has a contrast ratio of 2.25:1.", "axe:color-contrast"),
    issue("P2-10", "1.4.4", L, ".key-point", "The key point box has a fixed 44 px height with overflow hidden, so enlarged text is cut off.", None),
    issue("P2-11", "4.1.2", L, "#more-trigger", "The equation toggle is a div with aria-expanded and a click handler; no role and no keyboard access.", "axe:aria-allowed-attr", also=["2.1.1"]),
    issue("P2-12", "1.3.1", L, ".glossary", "The glossary ul contains div children instead of li.", "axe:list"),
    issue("P2-13", "1.4.4", L, 'meta[name="viewport"]', "The viewport disables zoom with user-scalable=no and maximum-scale=1.", "axe:meta-viewport"),
    issue("P2-14", "2.4.3", L, ".next-lesson", 'The Next lesson link has tabindex="1", so it receives focus first, before the skip link and navigation.', "engine:positive_tabindex"),
    issue("P2-15", "3.1.2", L, "#main > p:nth-of-type(2)", "An Indonesian sentence has no lang attribute.", None),
    issue("P2-16", "2.4.2", L, "title", 'The page title is only "Page".', None),
]
PR2_DECOYS = [
    decoy("D2-01", L, "video:has(track)", "1.2.2", "Video 2 has an English captions track."),
    decoy("D2-02", L, ".divider", "1.1.1", 'Decorative divider with alt="".'),
    decoy("D2-03", L, ".data-table:has(caption)", "1.3.1", "The second table has a caption and th with scope."),
    decoy("D2-04", L, '.further a[href="lesson.html#main"]', "2.4.4", 'Visible text "More" with aria-label "More about leaf structure"; the name is specific and contains the visible text (2.5.3).'),
    decoy("D2-05", L, ".divider", "2.3.3", "The divider fades slowly over 6 s and stops under prefers-reduced-motion."),
    decoy("D2-06", L, 'span[lang="id"]', "3.1.2", 'The Indonesian phrase in the following paragraph is marked lang="id".'),
]


def counts(issues, decoys):
    return {
        "issues": len(issues), "decoys": len(decoys),
        "engine_detectable": sum(1 for i in issues if i["engine_signal"]),
        "judgment_only": sum(1 for i in issues if not i["engine_signal"]),
        "by_principle": {p: sum(1 for i in issues if i["principle"] == p) for p in P.values()},
    }


def main():
    gt = {
        "schema_version": "1.0",
        "note": ("Planted issues and decoys in the OpenClass fixture, written by the same team that built CurbCut. "
                 "engine_signal is the deterministic check that fires on the element with axe-core 4.13.0 and the "
                 "CurbCut engine, or null when only judgment can find it."),
        "fixture_root": "codes/fixture/src",
        "changes": [
            "26 Sep 2026, after the first scoring run: P1-08 selector widened from the #terms-box container to include "
            "the two links that form the trap, as its description already said. P1-15 selector moved from the Sign up "
            "control to the instruction paragraph that contains the sensory wording. No issue was added, removed or re-scoped.",
        ],
        "prs": [
            {"id": "pr-1", "base": "main", "head": "demo/pr-1-quiz-signup", "counts": counts(PR1, PR1_DECOYS), "issues": PR1, "decoys": PR1_DECOYS},
            {"id": "pr-2", "base": "main", "head": "demo/pr-2-lesson-media", "counts": counts(PR2, PR2_DECOYS), "issues": PR2, "decoys": PR2_DECOYS},
        ],
    }
    out = Path(__file__).with_name("ground-truth.json")
    out.write_text(json.dumps(gt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    for pr in gt["prs"]:
        print(pr["id"], json.dumps(pr["counts"]))


if __name__ == "__main__":
    main()
