"""data.gov.in "Current Daily Price" mandi adapter (real source).

API: https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
(params: api-key, format=json, limit, filters[state|commodity], offset)

The free tier returns "records" with fields like:
    state, district, market, commodity, variety,
    min_price, max_price, modal_price ("-" when missing),
    arrival_date (dd/mm/yyyy)

Robustness rules (this is a flaky public API):
- transport injectable for contract tests (never live network in tests)
- any failure -> [] with logged error (endpoint then serves empty rows)
- "-" / blank / non-numeric prices -> skipped row (never fabricate 0)
- unparsable dates -> skipped row
"""

import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from app.providers.base import PriceObservation

logger = logging.getLogger(__name__)

RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
BASE_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"


def _parse_arrival_date(raw: str) -> datetime | None:
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(raw.strip(), fmt)
            return dt.replace(tzinfo=UTC)
        except (ValueError, AttributeError):
            continue
    return None


def _parse_price(raw: Any) -> float | None:
    if raw is None:
        return None
    text = str(raw).strip()
    if not text or text in {"-", "NA", "N/A", "nr"}:
        return None
    try:
        value = float(text.replace(",", ""))
        return value if value > 0 else None
    except ValueError:
        return None


class DataGovMandiPriceSource:
    name = "datagov"

    def __init__(
        self,
        api_key: str,
        transport: httpx.AsyncBaseTransport | None = None,
        base_url: str = BASE_URL,
        page_limit: int = 500,
    ) -> None:
        if not api_key:
            raise RuntimeError("DataGovMandiPriceSource requires DATAGOV_API_KEY")
        self._api_key = api_key
        self._base_url = base_url
        self._page_limit = page_limit
        self._client = httpx.AsyncClient(
            transport=transport,
            timeout=httpx.Timeout(10.0, connect=5.0),
        )

    async def fetch_daily(self, observation_date: datetime | None = None) -> list[PriceObservation]:
        rows: list[PriceObservation] = []
        offset = 0
        try:
            while True:
                resp = await self._client.get(
                    self._base_url,
                    params={
                        "api-key": self._api_key,
                        "format": "json",
                        "limit": self._page_limit,
                        "offset": offset,
                    },
                )
                resp.raise_for_status()
                payload = resp.json()
                records: list[dict[str, Any]] = payload.get("records") or []
                rows.extend(self._convert(r) for r in records if self._convert(r) is not None)
                total = int(payload.get("total_count") or payload.get("count") or 0)
                offset += len(records)
                if (
                    not records
                    or (total and offset >= total)
                    or (not total and len(records) < self._page_limit)
                    or offset >= 2000
                ):
                    break
            return rows
        except Exception:
            logger.exception("datagov fetch failed after %d rows", len(rows))
            return rows  # partial data is better than none; empty list on total failure

    def _convert(self, rec: dict[str, Any]) -> PriceObservation | None:
        try:
            state = (rec.get("state") or "").strip()
            district = (rec.get("district") or "").strip()
            market = (rec.get("market") or "").strip()
            commodity = (rec.get("commodity") or "").strip()
            min_price = _parse_price(rec.get("min_price"))
            max_price = _parse_price(rec.get("max_price"))
            modal_price = _parse_price(rec.get("modal_price"))
            date = _parse_arrival_date(rec.get("arrival_date", ""))
            if not (
                state and market and commodity and min_price and max_price and modal_price and date
            ):
                return None
            if modal_price < min_price or modal_price > max_price:
                return None
            return PriceObservation(
                market=market,
                district=district,
                state=state,
                commodity=commodity,
                variety=(rec.get("variety") or "").strip() or None,
                observation_date=date,
                min_price=min_price,
                max_price=max_price,
                modal_price=modal_price,
                source=self.name,
            )
        except Exception:
            logger.debug("skipping malformed record: %r", rec)
            return None
