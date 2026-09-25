"""Accessibility regression tests. Run them through the engine so base and head are compared:

    uv run --project codes/engine curbcut verify --id pr-1 --base <base> --head <head> --tests tests/a11y --out <verify.json>

Tests use pytest-playwright's `page` fixture and helpers from curbcut.testkit.
Name each file test_<report id without dash>_<finding id>.py, for example test_pr1_f003.py.
"""

import pytest


@pytest.fixture(autouse=True)
def _require_base_url(base_url):
    if not base_url:
        pytest.fail("No base URL. Run these tests with `curbcut verify`, which serves base and head for you.")
