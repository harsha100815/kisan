"""Phase 0 diagnosis endpoint.

Accepts an image + optional crop key, runs the configured VisionProvider via
DiagnosisService, and always returns the uncertainty-aware contract. With the
default null provider this returns status="unavailable" — proving the full path
(audit row included) without any external service.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.providers.registry import get_vision_provider
from app.schemas.diagnosis import DiagnosisResponse
from app.services.diagnosis_service import DiagnosisService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["diagnosis"])

MAX_IMAGE_BYTES = 8 * 1024 * 1024  # 8 MB pre-compression ceiling


@router.post("/diagnosis/diagnose", response_model=DiagnosisResponse)
async def diagnose(
    image: Annotated[UploadFile, File()],
    crop_key: Annotated[str | None, Form()] = None,
    language: Annotated[str, Form()] = "hi",
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> DiagnosisResponse:
    if image.size and image.size > MAX_IMAGE_BYTES:
        return _too_large()

    data = await image.read()
    if len(data) > MAX_IMAGE_BYTES:
        return _too_large()
    if not data:
        return DiagnosisResponse(
            audit_id="00000000-0000-0000-0000-000000000000",
            status="failed",
            provider=get_vision_provider().name,
            model_version=None,
        )

    service = DiagnosisService(get_vision_provider(), session)
    result = await service.diagnose(
        crop_key=crop_key,
        image_bytes=data,
        content_type=image.content_type or "image/jpeg",
        language=language,
    )
    result.pop("_disclaimer_text", None)
    return DiagnosisResponse(**result)


def _too_large() -> DiagnosisResponse:
    return DiagnosisResponse(
        audit_id="00000000-0000-0000-0000-000000000000",
        status="failed",
        provider="n/a",
        model_version=None,
    )


@router.get("/diagnosis/disclaimer")
async def disclaimer(language: str = "hi") -> dict[str, str]:
    """Localized disclaimer text; the mobile app must always render this."""
    from app.i18n.loader import t

    key = "diag.disclaimer.not_guaranteed"
    return {"key": key, "text": t(key, language)}
