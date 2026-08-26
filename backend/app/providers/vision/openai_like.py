"""OpenAI-compatible vision adapter skeleton.

Disabled unless OPENAI_API_KEY is configured. Kept as an example of how a real
adapter implements the VisionProvider Protocol. No network call happens in
Phase 0 tests; transport is injectable for contract testing later.
"""

import base64

from app.providers.base import (
    DiagnosisRequest,
    ProviderDiagnosisResult,
    RawPrediction,
)

SYSTEM_PROMPT = """You are a crop disease identification assistant for Indian
smallholder farmers. Answer ONLY with JSON: {"disease_key": one of the provided
catalogue keys or null, "confidence": 0..1, "alternatives": [...]}. Never invent
disease keys outside the catalogue."""


class OpenAILikeVisionProvider:
    name = "openai"

    def __init__(self, api_key: str | None, model: str = "gpt-4o-mini") -> None:
        if not api_key:
            raise RuntimeError("OpenAILikeVisionProvider requires OPENAI_API_KEY")
        self._api_key = api_key
        self._model = model

    async def diagnose(self, request: DiagnosisRequest) -> ProviderDiagnosisResult:
        # Phase 0: not wired to network. Real implementation will:
        # 1. build chat completion with image_url = data:<content_type>;base64,<...>
        # 2. parse strict JSON, clamp confidence into [0,1]
        # 3. map unknown disease_keys to None (never trust provider labels)
        encoded = base64.b64encode(request.image_bytes).decode()
        return ProviderDiagnosisResult(
            status="failed",
            prediction=RawPrediction(
                disease_key=None,
                confidence=None,
                model_version=self._model,
                raw={"note": "not_implemented", "image_bytes_b64_len": len(encoded)},
            ),
            provider=self.name,
            latency_ms=None,
            error_message="openai adapter not implemented in phase 0",
        )
