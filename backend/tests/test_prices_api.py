"""Contract tests for the mandi prices endpoint (stub source)."""

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.v1.router import router


def _app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


async def test_prices_today_returns_fixture_rows():
    async with AsyncClient(transport=ASGITransport(app=_app()), base_url="http://t") as client:
        resp = await client.get("/api/v1/prices/today")
    assert resp.status_code == 200
    body = resp.json()
    assert body["source"] == "stub"
    assert body["count"] == 3
    markets = {r["market"] for r in body["rows"]}
    assert "Badwani" in markets
    row = body["rows"][0]
    assert set(row) >= {"market", "commodity", "modal_price", "observation_date", "source"}


async def test_prices_today_commodity_filter_is_case_insensitive():
    async with AsyncClient(transport=ASGITransport(app=_app()), base_url="http://t") as client:
        resp = await client.get("/api/v1/prices/today", params={"commodity": "cotton"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 1
    assert body["rows"][0]["commodity"] == "Cotton"


async def test_prices_today_state_filter_and_empty_result():
    async with AsyncClient(transport=ASGITransport(app=_app()), base_url="http://t") as client:
        ok = await client.get("/api/v1/prices/today", params={"state": "maharashtra"})
        none = await client.get("/api/v1/prices/today", params={"state": "nowhere"})
    assert ok.json()["count"] == 1
    assert none.json()["count"] == 0
    assert none.json()["rows"] == []
