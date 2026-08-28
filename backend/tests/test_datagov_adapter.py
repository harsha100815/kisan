"""Contract tests for the real data.gov.in mandi adapter (mocked transport)."""

import httpx
import pytest

from app.providers.mandi.datagov import DataGovMandiPriceSource

GOOD_RECORD = {
    "state": "Madhya Pradesh",
    "district": "Badwani",
    "market": "Badwani",
    "commodity": "Soybean",
    "variety": "Yellow",
    "min_price": "4600",
    "max_price": "4900",
    "modal_price": "4771",
    "arrival_date": "26/08/2026",
}


def _transport(payload: dict | Exception) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        if isinstance(payload, Exception):
            raise payload
        return httpx.Response(200, json=payload)

    return httpx.MockTransport(handler)


def _payload(records: list[dict], total: int | None = None) -> dict:
    out = {"records": records}
    if total is not None:
        out["total_count"] = total
    return out


@pytest.mark.asyncio
async def test_parses_good_records():
    src = DataGovMandiPriceSource("k", transport=_transport(_payload([GOOD_RECORD])))
    rows = await src.fetch_daily()
    assert len(rows) == 1
    r = rows[0]
    assert r.market == "Badwani"
    assert r.modal_price == 4771
    assert r.source == "datagov"
    assert r.observation_date.year == 2026 and r.observation_date.month == 8


@pytest.mark.asyncio
async def test_skips_dash_prices_and_bad_dates():
    bad = {**GOOD_RECORD, "modal_price": "-", "arrival_date": "31/31/2026"}
    src = DataGovMandiPriceSource("k", transport=_transport(_payload([bad, GOOD_RECORD])))
    rows = await src.fetch_daily()
    assert len(rows) == 1


@pytest.mark.asyncio
async def test_network_error_returns_empty_not_crash():
    src = DataGovMandiPriceSource("k", transport=_transport(httpx.ConnectError("boom")))
    assert await src.fetch_daily() == []


@pytest.mark.asyncio
async def test_pagination_stops_at_total():
    def handler(request: httpx.Request) -> httpx.Response:
        offset = int(request.url.params.get("offset", 0))
        return httpx.Response(
            200, json={"records": [GOOD_RECORD] if offset == 0 else [GOOD_RECORD], "total_count": 2}
        )

    src = DataGovMandiPriceSource(
        "k",
        transport=httpx.MockTransport(handler),
    )
    rows = await src.fetch_daily()
    assert len(rows) == 2


@pytest.mark.asyncio
async def test_modal_outside_range_rejected():
    bad = {**GOOD_RECORD, "modal_price": "99999"}
    src = DataGovMandiPriceSource("k", transport=_transport(_payload([bad])))
    assert await src.fetch_daily() == []


def test_requires_api_key():
    with pytest.raises(RuntimeError):
        DataGovMandiPriceSource("")
