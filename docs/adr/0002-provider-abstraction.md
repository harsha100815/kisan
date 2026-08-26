# ADR 0002 — Provider Abstraction for External Services

Status: accepted · Date: 2026-08-25

## Context

Vision AI, SMS/OTP, WhatsApp, mandi price data, and object storage are all
expected to change vendor during the startup's life (cost, quality, compliance).
Business logic must not know vendors.

## Decision

Every external dependency is defined as a small `Protocol` in
`app/providers/base.py` with dataclass DTOs. Adapters implement Protocols;
`registry.py` factories select adapters from env vars and fail loudly on unknown
values. Business services accept Protocols only.

Current selection map:

| Interface | Values |
|---|---|
| `VISION_PROVIDER` | `null` (default) · `openai` |
| `SMS_PROVIDER` | `console` (default) · `msg91` (planned) |
| `WHATSAPP_PROVIDER` | `null` (default) · `cloud_api` (planned) |
| `MANDI_PRICE_SOURCE` | `stub` (default) · `datagov` (planned) |
| `STORAGE_PROVIDER` | `local` (default) · `s3` (planned) |

## Consequences

+ Vendor swap = new adapter class + one env var change.
+ Tests inject fakes trivially (see `tests/test_diagnosis_contract.py`).
− Small indirection cost; enforced by review.
