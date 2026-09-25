import asyncio

import pytest
from fastapi.testclient import TestClient

from app.db import create_tables, get_engine
from app.main import app
from app.settings import Settings, get_settings

TOKEN = "test-token"


def report(**kw):
    body = {
        "schema_version": "1.0", "id": "pr-1", "repo": "eziedutech/curbcut",
        "pr": {"base": "main", "head": "demo/pr-1-quiz-signup", "base_sha": "a" * 40, "head_sha": "b" * 40},
        "review": {
            "summary": {"proven": 1, "flagged": 1, "out_of_reach": 1, "not_scanned": 0},
            "findings": [{"id": "F001", "tier": "proven"}, {"id": "F002", "tier": "flagged"}],
            "out_of_reach": [{"sc": "1.2.2", "title": "Caption accuracy", "reason": "Not measurable."}],
            "not_scanned": [],
        },
        "verify": {"summary": {"verified": 3}},
    }
    body.update(kw)
    return body


@pytest.fixture
def client(tmp_path):
    url = f"sqlite+aiosqlite:///{tmp_path / 'test.db'}"
    settings = Settings(database_url=url, curbcut_ingest_token=TOKEN, git_sha="abc1234")
    asyncio.run(create_tables(url))
    app.dependency_overrides[get_settings] = lambda: settings
    yield TestClient(app)
    app.dependency_overrides.clear()
    asyncio.run(get_engine(url).dispose())


def test_health_reports_sha(client):
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["git_sha"] == "abc1234"


def test_ingest_requires_token(client):
    assert client.post("/api/reports/ingest", json=report()).status_code == 401
    assert client.post("/api/reports/ingest", json=report(), headers={"Authorization": "Bearer wrong"}).status_code == 401


def test_ingest_then_list_and_get(client):
    r = client.post("/api/reports/ingest", json=report(), headers={"Authorization": f"Bearer {TOKEN}"})
    assert r.status_code == 201
    items = client.get("/api/reports").json()
    assert [(i["id"], i["proven"], i["flagged"], i["verified_fixes"]) for i in items] == [("pr-1", 1, 1, 3)]
    full = client.get("/api/reports/pr-1").json()
    assert full["review"]["findings"][1]["id"] == "F002" and full["verify"]["summary"]["verified"] == 3


def test_reingest_replaces(client):
    h = {"Authorization": f"Bearer {TOKEN}"}
    client.post("/api/reports/ingest", json=report(), headers=h)
    newer = report(pr={"base": "main", "head": "demo/pr-1-quiz-signup", "base_sha": "a" * 40, "head_sha": "c" * 40})
    client.post("/api/reports/ingest", json=newer, headers=h)
    items = client.get("/api/reports").json()
    assert len(items) == 1 and items[0]["head_sha"] == "c" * 40


def test_summary_must_match_lists(client):
    bad = report()
    bad["review"]["summary"]["proven"] = 5
    r = client.post("/api/reports/ingest", json=bad, headers={"Authorization": f"Bearer {TOKEN}"})
    assert r.status_code == 422


def test_unknown_report_is_404(client):
    assert client.get("/api/reports/nope").status_code == 404
