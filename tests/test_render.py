from guess_explainr.routes.step4 import _render


def test_plain_text():
    assert "<p>Hello</p>" in _render("Hello")


def test_bold():
    assert "<strong>bold</strong>" in _render("**bold**")


def test_italic():
    assert "<em>note</em>" in _render("*note*")


def test_list_after_paragraph():
    # LLMs omit the blank line before lists — our regex must inject it
    html = _render("Here are some tips:\n* first\n* second")
    assert "<li>first</li>" in html
    assert "<li>second</li>" in html


def test_list_with_blank_line():
    assert "<li>item</li>" in _render("Intro\n\n* item")


def test_dash_list():
    html = _render("Intro\n- a\n- b")
    assert "<li>a</li>" in html
    assert "<li>b</li>" in html


def test_plus_list():
    html = _render("Intro\n+ x")
    assert "<li>x</li>" in html


def test_header_h2():
    assert "<h2>" in _render("## Title")


def test_header_h3():
    assert "<h3>" in _render("### Sub")


def test_empty_string():
    assert _render("") == ""
