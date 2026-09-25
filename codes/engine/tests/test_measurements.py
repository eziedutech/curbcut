"""Engine self-tests on small inline pages with known answers."""

from curbcut import browser


def test_contrast_matches_wcag_formula(page):
    page.set_content('<p id="a" style="color:#9a9a9a">grey</p><p id="b" style="color:#595959">dark</p>'
                     '<p id="c" style="color:#fff;background:#7fb3d5">cap</p>')
    assert browser.contrast_of(page, "#a")["ratio"] == 2.81
    assert browser.contrast_of(page, "#b")["ratio"] == 7.0
    assert browser.contrast_of(page, "#c")["ratio"] == 2.25


def test_background_image_is_not_guessed(page):
    page.set_content('<div style="background-image:linear-gradient(#000,#fff)"><p id="t">x</p></div>')
    c = browser.contrast_of(page, "#t")
    assert c["determinable"] is False and "background image" in c["reason"]


def test_focus_trap_detected(page):
    page.set_content('<a href="#" id="x">x</a><a href="#" id="a">a</a><a href="#" id="b">b</a><a href="#" id="y">y</a>'
                     "<script>b.onkeydown=e=>{if(e.key==='Tab'&&!e.shiftKey){e.preventDefault();a.focus()}}</script>")
    f = browser.analyse_focus(browser.focus_crawl(page))
    assert f["trap"]["cycle"] == ["#a", "#b"]
    assert f["trap"]["unreachable"] == ["#y"]


def test_no_trap_and_visible_focus(page):
    page.set_content("<style>:focus-visible{outline:3px solid red}</style><a href='#' id='a'>a</a><button id='b'>b</button>")
    f = browser.analyse_focus(browser.focus_crawl(page))
    assert f["trap"] is None and f["focus_not_visible"] == []


def test_missing_focus_indicator_detected(page):
    page.set_content("<style>button:focus{outline:none}</style><button id='b'>b</button>")
    assert browser.analyse_focus(browser.focus_crawl(page))["focus_not_visible"] == ["#b"]


def test_replaced_indicator_is_not_flagged(page):
    page.set_content("<style>button:focus{outline:none;box-shadow:0 0 0 3px blue}</style><button id='b'>b</button>")
    assert browser.analyse_focus(browser.focus_crawl(page))["focus_not_visible"] == []


def test_positive_tabindex_reported(page):
    page.set_content("<a href='#' id='a'>a</a><a href='#' id='n' tabindex='1'>n</a>")
    p = browser.analyse_focus(browser.focus_crawl(page))["positive_tabindex"]
    assert p == [{"selector": "#n", "tabindex": 1, "dom_position": 2, "focus_position": 1}]


def test_clickable_div_found(page):
    page.set_content("<div id='d'>go</div><button id='b'>ok</button><script>d.onclick=()=>1;b.onclick=()=>1</script>")
    assert [c["selector"] for c in browser.clickable_not_focusable(page)] == ["#d"]


def test_accessible_name_from_chromium(page):
    page.set_content("<button id='b' aria-label='Close quiz terms'><svg aria-hidden='true'></svg></button>")
    assert browser.ax_node(page, "#b") == {"name": "Close quiz terms", "role": "button", "ignored": False}


def test_narration_names_gaps_only_where_a_name_is_required():
    from curbcut.report import narrate
    snap = '- list:\n  - listitem\n- button\n- img "chart"\n- img\n- textbox "Email"\n- radio "Core" [checked]\n- heading "Quiz" [level=1]'
    assert narrate(snap) == ["list", "button, unlabeled", "img, chart", "img, no description",
                             "textbox, Email", "radio, Core, checked", "heading, Quiz, level 1"]
