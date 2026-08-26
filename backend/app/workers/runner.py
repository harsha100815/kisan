"""arq worker settings.

The worker shares the backend image and codebase; its role is selected by the
container command (`arq app.workers.runner.WorkerSettings`). Phase 0 ships a
heartbeat task proving the Redis round-trip. Ingestion/alerts/diagnosis jobs
plug in here in later phases.
"""

import logging

from redis.asyncio import Redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def startup(ctx: dict) -> None:
    settings = get_settings()
    ctx["redis"] = Redis.from_url(settings.REDIS_URL)
    logger.info("worker started; env=%s", settings.APP_ENV)


async def shutdown(ctx: dict) -> None:
    redis: Redis | None = ctx.get("redis")
    if redis is not None:
        await redis.aclose()
    logger.info("worker stopped")


async def heartbeat(ctx: dict) -> str:
    """Prove queue round-trip: enqueue self-check via redis ping."""
    redis: Redis = ctx["redis"]
    pong = await redis.ping()
    return f"heartbeat ok (redis ping -> {pong})"


class WorkerSettings:
    functions = [heartbeat]
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 4
    job_timeout = 60
