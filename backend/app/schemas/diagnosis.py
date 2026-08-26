from typing import Literal

from pydantic import BaseModel, Field


class HealthStatus(BaseModel):
    status: Literal["ok"] = "ok"
    env: str
    version: str


class ReadinessCheck(BaseModel):
    component: str
    ok: bool
    detail: str | None = None


class ReadinessReport(BaseModel):
    ready: bool
    checks: list[ReadinessCheck]


class DiseasePrediction(BaseModel):
    disease_key: str | None = Field(
        description="Stable catalogue key; null when no confident match exists."
    )
    confidence: float | None = Field(ge=0.0, le=1.0)


class DiagnosisResponse(BaseModel):
    """Contract: an AI diagnosis is ALWAYS provisional.

    - is_definitive is false by construction in this phase.
    - confidence_band must be shown to users alongside any prediction.
    - disclaimer_key points to localized copy that must accompany results.
    """

    audit_id: str
    status: Literal["completed", "unavailable", "failed"]
    is_definitive: bool = False
    confidence_band: Literal["high", "medium", "low"] | None = None
    prediction: DiseasePrediction | None = None
    alternatives: list[DiseasePrediction] = Field(default_factory=list)
    provider: str
    model_version: str | None = None
    disclaimer_key: str = "diag.disclaimer.not_guaranteed"


class DiagnoseAccepted(BaseModel):
    audit_id: str
    status: str
    detail: str
