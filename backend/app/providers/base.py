"""Provider interfaces (Protocols) for every external dependency.

Business logic depends ONLY on these Protocols. Concrete adapters live in
subpackages and are selected via environment variables by app/providers/registry.py.
Swapping vendors must never require touching business logic. See ADR 0002.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol, runtime_checkable


@dataclass(slots=True)
class DiagnosisRequest:
    crop_key: str | None
    image_bytes: bytes
    content_type: str = "image/jpeg"
    language: str = "hi"


@dataclass(slots=True)
class RawPrediction:
    """Provider-native output before business validation/mapping."""

    disease_key: str | None
    confidence: float | None  # 0..1, None if provider gives none
    alternatives: list[dict[str, Any]] = field(default_factory=list)
    model_version: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderDiagnosisResult:
    """Result envelope returned to the service layer."""

    status: str  # completed | unavailable | failed
    prediction: RawPrediction | None
    provider: str
    latency_ms: int | None
    error_message: str | None = None


@runtime_checkable
class VisionProvider(Protocol):
    name: str

    async def diagnose(self, request: DiagnosisRequest) -> ProviderDiagnosisResult: ...


@dataclass(slots=True)
class SendResult:
    ok: bool
    provider_message_id: str | None = None
    error: str | None = None


@runtime_checkable
class SMSProvider(Protocol):
    name: str

    async def send_otp(self, phone: str, code: str) -> SendResult: ...


@runtime_checkable
class WhatsAppClient(Protocol):
    name: str

    async def send_text(self, phone: str, text: str) -> SendResult: ...

    async def send_image_document(self, phone: str, image_ref: str, caption: str) -> SendResult: ...


@dataclass(slots=True)
class PriceObservation:
    market: str
    district: str
    state: str
    commodity: str
    variety: str | None
    observation_date: datetime
    min_price: float  # ₹/quintal
    max_price: float
    modal_price: float
    source: str


@runtime_checkable
class MandiPriceSource(Protocol):
    name: str

    async def fetch_daily(
        self,
        observation_date: datetime | None = None,
    ) -> list[PriceObservation]: ...


@runtime_checkable
class ObjectStorage(Protocol):
    name: str

    async def put(self, key: str, data: bytes, content_type: str) -> str:
        """Store bytes and return a reference usable later for retrieval."""
        ...
