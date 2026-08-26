"""Phase 1 entry point: daily mandi prices.

Serves today's price observations from the configured MandiPriceSource.
With the default stub source this returns a small deterministic fixture —
the real data.gov.in adapter slots in later without contract changes.
"""

import logging
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Query

from app.providers.base import PriceObservation
from app.providers.registry import get_mandi_price_source

logger = logging.getLogger(__name__)
router = APIRouter(tags=["prices"])


def _serialize(obs: PriceObservation) -> dict:
    return {
        "market": obs.market,
        "district": obs.district,
        "state": obs.state,
        "commodity": obs.commodity,
        "variety": obs.variety,
        "observation_date": obs.observation_date.isoformat(),
        "min_price": obs.min_price,
        "max_price": obs.max_price,
        "modal_price": obs.modal_price,
        "source": obs.source,
    }


@router.get("/prices/today")
async def prices_today(
    commodity: Annotated[str | None, Query(description="Filter by commodity name")] = None,
    state: Annotated[str | None, Query(description="Filter by state name")] = None,
) -> dict:
    """Today's mandi observations; optional case-insensitive filters."""
    source = get_mandi_price_source()
    try:
        rows = await source.fetch_daily(datetime.now(UTC))
    except Exception:
        logger.exception("mandi price source %s failed", source.name)
        return {
            "source": source.name,
            "date": datetime.now(UTC).date().isoformat(),
            "count": 0,
            "rows": [],
        }

    if commodity:
        wanted = commodity.lower()
        rows = [r for r in rows if r.commodity.lower() == wanted]
    if state:
        wanted = state.lower()
        rows = [r for r in rows if r.state.lower() == wanted]

    return {
        "source": source.name,
        "date": datetime.now(UTC).date().isoformat(),
        "count": len(rows),
        "rows": [_serialize(r) for r in rows],
    }
