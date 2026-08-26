"""Null vision provider: Phase 0 default.

Returns an explicit "unavailable" result with no prediction. Guarantees:
- the API contract works end-to-end without any external service,
- nothing is ever presented to a farmer as a real diagnosis,
- audit trail rows are still written (status=unavailable).
"""

from app.providers.base import (
    DiagnosisRequest,
    ProviderDiagnosisResult,
    RawPrediction,
)


class NullVisionProvider:
    name = "null"

    async def diagnose(self, request: DiagnosisRequest) -> ProviderDiagnosisResult:
        return ProviderDiagnosisResult(
            status="unavailable",
            prediction=RawPrediction(
                disease_key=None,
                confidence=None,
                alternatives=[],
                model_version="none",
                raw={"reason": "vision_provider_disabled"},
            ),
            provider=self.name,
            latency_ms=None,
            error_message=None,
        )
