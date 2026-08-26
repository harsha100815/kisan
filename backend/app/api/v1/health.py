import time

from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import get_sessionmaker
from app.schemas.health import HealthStatus, ReadinessCheck, ReadinessReport

router = APIRouter(tags=["health"])
_started = time.monotonic()


@router.get("/health", response_model=HealthStatus)
async def liveness() -> HealthStatus:
    settings = get_settings()
    return HealthStatus(env=settings.APP_ENV, version="0.1.0")


@router.get("/health/ready", response_model=ReadinessReport)
async def readiness() -> ReadinessReport:
    checks: list[ReadinessCheck] = []

    try:
        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            await session.execute(text("SELECT 1"))
        checks.append(ReadinessCheck(component="postgres", ok=True))
    except Exception as exc:  # noqa: BLE001 — report, don't crash the probe
        checks.append(ReadinessCheck(component="postgres", ok=False, detail=str(exc)))

    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(get_settings().REDIS_URL)
        try:
            await client.ping()
        finally:
            await client.aclose()
        checks.append(ReadinessCheck(component="redis", ok=True))
    except Exception as exc:  # noqa: BLE001
        checks.append(ReadinessCheck(component="redis", ok=False, detail=str(exc)))

    return ReadinessReport(
        ready=all(c.ok for c in checks),
        checks=checks,
    )
