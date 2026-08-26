"""Diagnosis audit trail.

Every diagnosis attempt — success, low-confidence, provider outage, or parse
failure — writes exactly one row here. The row preserves raw provider output so
results are reproducible and reviewable. See docs/adr/0003.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

# Confidence bands: we never expose raw floats to farmers without a band.
CONFIDENCE_BANDS = ("high", "medium", "low")


def _uuid() -> PGUUID:
    return PGUUID(as_uuid=True)


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id: Mapped[uuid.UUID] = mapped_column(_uuid(), primary_key=True, default=uuid.uuid4)

    # Nullable until auth exists; diagnoses may arrive via WhatsApp bot unauthenticated.
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    crop_key: Mapped[str | None] = mapped_column(String(50))
    image_ref: Mapped[str | None] = mapped_column(String(500))

    # pending/completed/failed/unavailable
    status: Mapped[str] = mapped_column(String(20), default="pending")
    predicted_disease_key: Mapped[str | None] = mapped_column(String(100))
    confidence: Mapped[float | None] = mapped_column(Float)
    confidence_band: Mapped[str | None] = mapped_column(String(10))  # high/medium/low
    is_definitive: Mapped[bool] = mapped_column(default=False)  # always False in Phase 0
    alternatives: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)

    # Audit trail fields
    provider: Mapped[str] = mapped_column(String(30))
    model_version: Mapped[str | None] = mapped_column(String(100))
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text)
    raw_response: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
