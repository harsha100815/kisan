"""Diagnosis business logic.

Depends only on the VisionProvider Protocol — never on a concrete vendor SDK.
Every call path (success, low confidence, provider failure) writes an audit row
before returning. Confidence is banded; results are never definitive.
See docs/adr/0002 and 0003.
"""

import time
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.i18n.loader import t
from app.models.diagnosis import Diagnosis
from app.providers.base import DiagnosisRequest, VisionProvider

BAND_HIGH = 0.85
BAND_MEDIUM = 0.60


def band_for(confidence: float | None) -> str | None:
    if confidence is None:
        return None
    if confidence >= BAND_HIGH:
        return "high"
    if confidence >= BAND_MEDIUM:
        return "medium"
    return "low"


class DiagnosisService:
    def __init__(self, vision: VisionProvider, session: AsyncSession):
        self._vision = vision
        self._session = session

    async def diagnose(
        self,
        *,
        crop_key: str | None,
        image_bytes: bytes,
        content_type: str,
        language: str,
        user_id: uuid.UUID | None = None,
    ) -> dict:
        request = DiagnosisRequest(
            crop_key=crop_key,
            image_bytes=image_bytes,
            content_type=content_type,
            language=language,
        )

        audit = Diagnosis(
            user_id=user_id,
            crop_key=crop_key,
            status="pending",
            provider=self._vision.name,
        )
        self._session.add(audit)
        await self._session.flush()  # assign audit.id before provider call

        start = time.monotonic()
        try:
            result = await self._vision.diagnose(request)
        except Exception as exc:  # noqa: BLE001 — provider crashes must still be audited
            audit.status = "failed"
            audit.error_message = f"{type(exc).__name__}: {exc}"
            await self._session.commit()
            raise

        latency_ms = int((time.monotonic() - start) * 1000)

        prediction = result.prediction
        confidence = prediction.confidence if prediction else None
        disease_key = prediction.disease_key if prediction else None

        audit.provider = result.provider
        audit.model_version = prediction.model_version if prediction else None
        audit.latency_ms = latency_ms
        audit.raw_response = prediction.raw if prediction else None

        if result.status == "completed" and disease_key and confidence is not None:
            audit.status = "completed"
            audit.predicted_disease_key = disease_key
            audit.confidence = confidence
            audit.confidence_band = band_for(confidence)
            audit.is_definitive = False  # by policy, in every phase
            audit.alternatives = [
                {"disease_key": alt.get("disease_key"), "confidence": alt.get("confidence")}
                for alt in (prediction.alternatives or [])
            ]
        elif result.status == "completed":
            # Provider answered but gave nothing usable → treat as unavailable.
            audit.status = "unavailable"
            audit.error_message = "provider returned no usable prediction"
        else:
            audit.status = result.status  # unavailable / failed
            audit.error_message = result.error_message

        await self._session.commit()

        disclaimer = t("diag.disclaimer.not_guaranteed", language)
        return {
            "audit_id": str(audit.id),
            "status": audit.status,
            "is_definitive": False,
            "confidence_band": audit.confidence_band,
            "prediction": (
                {"disease_key": audit.predicted_disease_key, "confidence": audit.confidence}
                if audit.predicted_disease_key
                else None
            ),
            "alternatives": audit.alternatives or [],
            "provider": audit.provider,
            "model_version": audit.model_version,
            "disclaimer_key": "diag.disclaimer.not_guaranteed",
            "_disclaimer_text": disclaimer,  # internal convenience; API layer decides exposure
        }
