import hmac
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.db import Report, create_tables, session_factory
from app.settings import Settings, get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("backpy")


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    if settings.database_url:
        try:
            await create_tables(settings.database_url)
        except Exception:  # noqa: BLE001 - logged; health reports the database as unavailable
            log.exception("could not create tables; report routes will fail until DATABASE_URL works")
    else:
        log.warning("DATABASE_URL is not set; report routes will answer 503")
    yield


app = FastAPI(title="CurbCut backpy", docs_url="/api/docs", openapi_url="/api/openapi.json", lifespan=lifespan)


class Health(BaseModel):
    status: Literal["ok"] = "ok"
    service: Literal["backpy"] = "backpy"
    env: str
    git_sha: str
    database: bool
    ingest: bool


@app.get("/api/health", response_model=Health)
def health(settings: Settings = Depends(get_settings)) -> Health:
    return Health(env=settings.app_env, git_sha=settings.git_sha,
                  database=bool(settings.database_url), ingest=bool(settings.curbcut_ingest_token))


class PullRequest(BaseModel):
    base: str
    head: str
    base_sha: str
    head_sha: str


class FindingsSummary(BaseModel):
    proven: int = Field(ge=0)
    flagged: int = Field(ge=0)
    out_of_reach: int = Field(ge=0)
    not_scanned: int = Field(ge=0)


class ReviewBody(BaseModel):
    summary: FindingsSummary
    findings: list[dict[str, Any]]
    out_of_reach: list[dict[str, Any]]
    not_scanned: list[dict[str, Any]]


class ReportIn(BaseModel):
    """The report assembled by `curbcut report`. Only the fields the API relies on are checked."""

    model_config = {"extra": "allow"}

    schema_version: Literal["1.0"]
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{0,63}$")
    repo: str = Field(min_length=3, max_length=200)
    pr: PullRequest
    review: ReviewBody


class ReportListItem(BaseModel):
    id: str
    repo: str
    head: str
    head_sha: str
    received_at: datetime
    proven: int
    flagged: int
    out_of_reach: int
    not_scanned: int
    verified_fixes: int | None


def _require_db(settings: Settings) -> str:
    if not settings.database_url:
        raise HTTPException(503, "Report storage is not configured.")
    return settings.database_url


def _list_item(r: Report) -> ReportListItem:
    s = r.body["review"]["summary"]
    verify = r.body.get("verify")
    return ReportListItem(
        id=r.id, repo=r.repo, head=r.head, head_sha=r.head_sha, received_at=r.received_at,
        proven=s["proven"], flagged=s["flagged"], out_of_reach=s["out_of_reach"], not_scanned=s["not_scanned"],
        verified_fixes=verify["summary"]["verified"] if verify else None,
    )


@app.post("/api/reports/ingest", status_code=201)
async def ingest(report: ReportIn, authorization: str = Header(default=""),
                 settings: Settings = Depends(get_settings)) -> dict[str, str]:
    if not settings.curbcut_ingest_token:
        raise HTTPException(503, "Ingest is not configured.")
    supplied = authorization.removeprefix("Bearer ").strip()
    if not hmac.compare_digest(supplied.encode(), settings.curbcut_ingest_token.encode()):
        raise HTTPException(401, "Invalid ingest token.")
    s = report.review.summary
    tiers = [f.get("tier") for f in report.review.findings]
    if (s.proven, s.flagged, s.out_of_reach, s.not_scanned) != (
            tiers.count("proven"), tiers.count("flagged"), len(report.review.out_of_reach), len(report.review.not_scanned)):
        # A summary that disagrees with its own lists would put wrong numbers on the dashboard.
        raise HTTPException(422, "Summary counts do not match the lists.")
    url = _require_db(settings)
    body = report.model_dump(mode="json")
    async with session_factory(url)() as session:
        row = await session.get(Report, report.id)
        if row is None:
            row = Report(id=report.id)
            session.add(row)
        row.repo, row.head, row.head_sha, row.body = report.repo, report.pr.head, report.pr.head_sha, body
        await session.commit()
    async with session_factory(url)() as session:
        # Read back from the database: success is what is stored, not the absence of an error.
        stored = await session.get(Report, report.id)
        if stored is None or stored.head_sha != report.pr.head_sha:
            raise HTTPException(500, "Report was not stored.")
    log.info("ingested report %s for %s at %s", report.id, report.repo, report.pr.head_sha[:7])
    return {"id": report.id, "head_sha": report.pr.head_sha}


@app.get("/api/reports", response_model=list[ReportListItem])
async def list_reports(settings: Settings = Depends(get_settings)) -> list[ReportListItem]:
    url = _require_db(settings)
    async with session_factory(url)() as session:
        rows = (await session.scalars(select(Report).order_by(Report.received_at.desc()))).all()
    return [_list_item(r) for r in rows]


@app.get("/api/reports/{report_id}")
async def get_report(report_id: str, settings: Settings = Depends(get_settings)) -> dict[str, Any]:
    url = _require_db(settings)
    async with session_factory(url)() as session:
        row = await session.get(Report, report_id)
    if row is None:
        raise HTTPException(404, "No report with that id.")
    return {**row.body, "received_at": row.received_at.isoformat()}
