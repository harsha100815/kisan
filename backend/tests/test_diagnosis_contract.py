"""Contract tests: the diagnosis API with the default (null) provider.

Guarantees the uncertainty + audit contract holds even when no vision vendor
is configured:
- status is "unavailable", never a fake diagnosis
- is_definitive is always False
- a disclaimer key is always present
- an audit row exists in the database for every call
"""

from app.models.diagnosis import Diagnosis
from app.providers.base import (
    DiagnosisRequest,
    ProviderDiagnosisResult,
    RawPrediction,
)
from app.services.diagnosis_service import DiagnosisService, band_for

PNG_1PX = bytes.fromhex(
    "89504e470d0a1a0a0000000d494844520000000100000001080600000"
    "01f15c4890000000d49444154789c626001000000ffff030000060005"
    "57bfabd40000000049454e44ae426082"
)


async def test_diagnose_with_null_provider_returns_unavailable(client):
    resp = await client.post(
        "/api/v1/diagnosis/diagnose",
        files={"image": ("leaf.png", PNG_1PX, "image/png")},
        data={"crop_key": "cotton", "language": "hi"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "unavailable"
    assert body["is_definitive"] is False
    assert body["prediction"] is None
    assert body["disclaimer_key"] == "diag.disclaimer.not_guaranteed"


async def test_diagnose_writes_audit_row(client, db_sessionmaker):
    resp = await client.post(
        "/api/v1/diagnosis/diagnose",
        files={"image": ("leaf.png", PNG_1PX, "image/png")},
        data={"crop_key": "cotton"},
    )
    audit_id = resp.json()["audit_id"]
    async with db_sessionmaker() as session:
        row = await session.get(Diagnosis, __import__("uuid").UUID(audit_id))
        assert row is not None
        assert row.status == "unavailable"
        assert row.provider == "null"
        assert row.is_definitive is False


class _FakeProvider:
    name = "fake"

    def __init__(self, status="completed", key="leaf_curl", confidence=0.42):
        self.status = status
        self.key = key
        self.confidence = confidence

    async def diagnose(self, request: DiagnosisRequest) -> ProviderDiagnosisResult:
        return ProviderDiagnosisResult(
            status=self.status,
            prediction=RawPrediction(
                disease_key=self.key,
                confidence=self.confidence,
                alternatives=[{"disease_key": "alternaria_leaf_blight", "confidence": 0.11}],
                model_version="fake-v1",
                raw={"echo_crop": request.crop_key},
            ),
            provider=self.name,
            latency_ms=12,
        )


async def test_low_confidence_is_banded_not_definitive(client, db_sessionmaker):
    """A completed-but-uncertain provider result must carry band 'low' and stay provisional."""
    async with db_sessionmaker() as session:
        service = DiagnosisService(_FakeProvider(confidence=0.42), session)
        result = await service.diagnose(
            crop_key="cotton",
            image_bytes=PNG_1PX,
            content_type="image/png",
            language="en",
        )
        assert result["status"] == "completed"
        assert result["confidence_band"] == "low"
        assert result["is_definitive"] is False
        assert result["alternatives"][0]["disease_key"] == "alternaria_leaf_blight"

        row = await session.get(Diagnosis, __import__("uuid").UUID(result["audit_id"]))
        assert row.raw_response == {"echo_crop": "cotton"}
        assert row.model_version == "fake-v1"


async def test_provider_crash_is_audited_and_raised(db_sessionmaker):
    class Boom:
        name = "boom"

        async def diagnose(self, request):
            raise RuntimeError("provider exploded")

    session = db_sessionmaker()
    service = DiagnosisService(Boom(), session)
    import pytest as _pytest

    with _pytest.raises(RuntimeError):
        await service.diagnose(
            crop_key=None,
            image_bytes=b"x",
            content_type="image/png",
            language="hi",
        )
    await session.close()


def test_band_boundaries():
    assert band_for(0.9) == "high"
    assert band_for(0.7) == "medium"
    assert band_for(0.3) == "low"
    assert band_for(None) is None


def test_unknown_provider_name_fails_loudly(monkeypatch):
    from app.core.config import Settings
    from app.providers.registry import get_vision_provider

    settings = Settings(VISION_PROVIDER="does-not-exist", DATABASE_URL="sqlite+aiosqlite://")
    try:
        get_vision_provider(settings)
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "VISION_PROVIDER" in str(exc)
