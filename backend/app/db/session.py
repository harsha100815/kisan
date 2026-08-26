import re
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def _sanitize_url(url: str) -> str:
    # Tests may use sqlite+aiosqlite; keep driver handling in one place.
    return url


def get_engine() -> AsyncEngine:
    global _engine, _sessionmaker
    if _engine is None or _sessionmaker is None:
        settings = get_settings()
        _engine = create_async_engine(_sanitize_url(settings.DATABASE_URL), pool_pre_ping=True)
        _sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    get_engine()
    assert _sessionmaker is not None
    return _sessionmaker


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding a database session."""
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        yield session


def reset_engine() -> None:
    """Used by tests to rebind the engine to an isolated database URL."""
    global _engine, _sessionmaker
    _engine = None
    _sessionmaker = None


def mask_url(url: str) -> str:
    """Mask credentials in a database URL for logging."""
    return re.sub(r"://([^:@/]+):[^@/]+@", r"://\1:***@", url)
