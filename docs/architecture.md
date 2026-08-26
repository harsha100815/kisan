# Architecture Overview (Phase 0)

## System shape

```
Android app (Expo) ──HTTPS──► FastAPI ──► PostgreSQL (RDS-ready)
        │                        │  └────► Redis (cache / arq queue)
        └──WhatsApp (Phase 1+)   │
                                 ▼
                    Provider layer (app/providers)
                    vision · sms · whatsapp · mandi · storage
```

- **One backend image, two roles:** the API runs `uvicorn`, background work runs
  `arq` with the same codebase and config (`backend/app/workers/`).
- **Everything external is behind a Protocol** (`app/providers/base.py`) selected
  by env vars (`app/providers/registry.py`). Phase 0 ships safe defaults:
  `null` vision, `console` SMS, `null` WhatsApp, `stub` mandi source, local disk
  storage.
- **Localization is architectural**, not cosmetic: canonical locale JSON lives in
  `shared/i18n/locales`; both apps consume it. Hindi/English now; Telugu etc. are
  data-only additions.

## Key decisions (ADRs)

| ADR | Decision |
|---|---|
| [0001](adr/0001-monorepo-layout.md) | Monorepo layout & worker placement |
| [0002](adr/0002-provider-abstraction.md) | Vendor isolation via Protocols + registry |
| [0003](adr/0003-diagnosis-uncertainty-audit.md) | Uncertainty-aware diagnoses + audit trail |
| [0004](adr/0004-localization-strategy.md) | Shared locale files, fallback chains |

## Data model (initial migration only)

`users` — phone-first identity, preferred language (BCP-47 style codes).
`diagnoses` — full audit trail per diagnosis attempt: status, banded confidence,
provider/model version, latency, raw response, error. `is_definitive=false` by policy.

Full schema (markets, prices, alerts, content) arrives in Phase 1.

## Deliberately deferred

Auth/OTP flow · mandi ingestion pipeline · real vision providers · WhatsApp bot ·
alerts engine · advisory CMS · payments/marketplace. Each lands behind its provider
interface without rework of existing layers.
