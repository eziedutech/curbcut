"""One table: a review report per id, stored as the JSON the engine assembled.

The API never rewrites a report's content. It stores what was ingested and
derives the list view from it, so what the dashboard shows is what CI produced.
"""

from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    repo: Mapped[str] = mapped_column(String(200))
    head: Mapped[str] = mapped_column(String(200))
    head_sha: Mapped[str] = mapped_column(String(64))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    body: Mapped[dict] = mapped_column(JSON)


@lru_cache
def get_engine(url: str) -> AsyncEngine:
    return create_async_engine(url, pool_pre_ping=True)


def session_factory(url: str) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(url), expire_on_commit=False)


async def create_tables(url: str) -> None:
    async with get_engine(url).begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
