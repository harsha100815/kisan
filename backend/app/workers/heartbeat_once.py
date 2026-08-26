"""Run the worker heartbeat once, for local smoke testing.

Usage: python -m app.workers.heartbeat_once
"""

import asyncio

from redis.asyncio import Redis

from app.core.config import get_settings
from app.workers.runner import heartbeat


async def main() -> None:
    settings = get_settings()
    ctx = {"redis": Redis.from_url(settings.REDIS_URL)}
    try:
        result = await heartbeat(ctx)
        print(result)
    finally:
        await ctx["redis"].aclose()


if __name__ == "__main__":
    asyncio.run(main())
