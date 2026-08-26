from pydantic import BaseModel


class HealthStatus(BaseModel):
    status: str = "ok"
    env: str
    version: str


class ReadinessCheck(BaseModel):
    component: str
    ok: bool
    detail: str | None = None


class ReadinessReport(BaseModel):
    ready: bool
    checks: list[ReadinessCheck]
