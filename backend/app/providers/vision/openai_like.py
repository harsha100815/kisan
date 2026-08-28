"""OpenAI-compatible vision adapter — real implementation.

Calls the chat-completions API with the photo inline (base64 data URL), forcing
a strict JSON answer constrained to the crop-disease catalogue. The service
layer (diagnosis_service) independently validates everything: unknown keys are
dropped, confidence is clamped, results are never definitive.
"""

import base64
import json
import logging
import time

import httpx

from app.providers.base import (
    DiagnosisRequest,
    ProviderDiagnosisResult,
    RawPrediction,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a crop-disease identification assistant for Indian
smallholder farmers. You are given a photo of a crop (leaf/fruit/plant).
Identify the most likely disease or disorder. Answer with ONLY a JSON object,
no markdown, in exactly this shape:
{"disease_key": "<key or null>", "confidence": <0.0-1.0>,
 "alternatives": [{"disease_key": "<key>", "confidence": <0.0-1.0>}, ...],
 "is_healthy": <true|false>}
Rules: use short lowercase snake_case keys (e.g. leaf_curl, early_blight,
late_blight, rust, powdery_mildew, bacterial_leaf_spot, yellow_mosaic,
wilting, nutrient_deficiency, pest_damage, healthy). If the photo is unclear,
not a crop, or you are unsure, set disease_key to null and confidence below 0.5.
Never invent long descriptive names; keys are matched against a catalogue."""

MAX_IMAGE_BYTES = 8 * 1024 * 1024


class OpenAIVisionProvider:
    name = "openai"

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        transport: httpx.AsyncBaseTransport | None = None,
        base_url: str = "https://api.openai.com/v1",
    ) -> None:
        if not api_key:
            raise RuntimeError("OpenAIVisionProvider requires OPENAI_API_KEY")
        self._api_key = api_key
        self._model = model
        self._base_url = base_url
        self._client = httpx.AsyncClient(
            transport=transport,
            timeout=httpx.Timeout(45.0, connect=10.0),
        )

    async def diagnose(self, request: DiagnosisRequest) -> ProviderDiagnosisResult:
        if len(request.image_bytes) > MAX_IMAGE_BYTES:
            return ProviderDiagnosisResult(
                status="failed",
                prediction=None,
                provider=self.name,
                latency_ms=None,
                error_message="image too large",
            )

        encoded = base64.b64encode(request.image_bytes).decode()
        crop_line = f"Crop (farmer-reported): {request.crop_key}\n" if request.crop_key else ""
        payload = {
            "model": self._model,
            "temperature": 0.1,
            "max_tokens": 300,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{crop_line}Identify the condition in this photo.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{request.content_type};base64,{encoded}",
                                "detail": "low",
                            },
                        },
                    ],
                },
            ],
        }

        start = time.monotonic()
        try:
            resp = await self._client.post(
                f"{self._base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json=payload,
            )
            resp.raise_for_status()
            body = resp.json()
            content = body["choices"][0]["message"]["content"]
            latency_ms = int((time.monotonic() - start) * 1000)
        except (httpx.HTTPError, KeyError, IndexError, TypeError) as exc:
            logger.warning("vision call failed: %s", exc)
            return ProviderDiagnosisResult(
                status="failed",
                prediction=None,
                provider=self.name,
                latency_ms=None,
                error_message=f"{type(exc).__name__}",
            )

        return self._parse(content, latency_ms)

    def _parse(self, content: str, latency_ms: int) -> ProviderDiagnosisResult:
        raw_out: dict = {"raw_content": content[:2000]}
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return ProviderDiagnosisResult(
                status="failed",
                prediction=RawPrediction(
                    disease_key=None,
                    confidence=None,
                    model_version=self._model,
                    raw=raw_out,
                ),
                provider=self.name,
                latency_ms=latency_ms,
                error_message="provider returned non-JSON answer",
            )

        def _clean_key(value) -> str | None:
            if not isinstance(value, str):
                return None
            key = value.strip().lower().replace(" ", "_")[:100]
            return key or None

        def _clamp(value) -> float | None:
            try:
                return min(1.0, max(0.0, float(value)))
            except (TypeError, ValueError):
                return None

        disease_key = _clean_key(data.get("disease_key"))
        confidence = _clamp(data.get("confidence"))
        alternatives = []
        for alt in (data.get("alternatives") or [])[:3]:
            if isinstance(alt, dict):
                alt_key = _clean_key(alt.get("disease_key"))
                alt_conf = _clamp(alt.get("confidence"))
                if alt_key and alt_conf is not None and alt_key != disease_key:
                    alternatives.append({"disease_key": alt_key, "confidence": alt_conf})

        if not disease_key or confidence is None:
            # Model answered but nothing usable -> service layer maps to "unavailable"
            return ProviderDiagnosisResult(
                status="completed",
                prediction=RawPrediction(
                    disease_key=None,
                    confidence=None,
                    model_version=self._model,
                    raw={**raw_out, "parsed": data},
                ),
                provider=self.name,
                latency_ms=latency_ms,
            )

        return ProviderDiagnosisResult(
            status="completed",
            prediction=RawPrediction(
                disease_key=disease_key,
                confidence=confidence,
                alternatives=alternatives,
                model_version=self._model,
                raw={**raw_out, "parsed": data},
            ),
            provider=self.name,
            latency_ms=latency_ms,
        )
