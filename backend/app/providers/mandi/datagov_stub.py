"""Deterministic stub mandi price source for local development and tests.

Emits a tiny fixed fixture so the ingestion/alert pipeline can be built and
tested before the data.gov.in adapter exists.
"""

from datetime import UTC, datetime

from app.providers.base import PriceObservation

_FIXTURE = [
    # (market, district, state, commodity, variety, min, max, modal)
    ("Badwani", "Badwani", "Madhya Pradesh", "Soybean", "Yellow", 4600, 4900, 4771),
    ("Khargone", "Khargone", "Madhya Pradesh", "Soybean", "Yellow", 4550, 4880, 4720),
    ("Akot", "Akola", "Maharashtra", "Cotton", "Kapas", 6900, 7500, 7205),
]


class StubMandiPriceSource:
    name = "stub"

    async def fetch_daily(self, observation_date: datetime | None = None) -> list[PriceObservation]:
        date = observation_date or datetime.now(UTC)
        return [
            PriceObservation(
                market=m,
                district=d,
                state=s,
                commodity=c,
                variety=v,
                observation_date=date,
                min_price=lo,
                max_price=hi,
                modal_price=mo,
                source=self.name,
            )
            for (m, d, s, c, v, lo, hi, mo) in _FIXTURE
        ]
