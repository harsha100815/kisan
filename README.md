# Kisan Sahayak (किसान सहायक)

Agri-tech MVP for Indian smallholder farmers: **daily mandi prices** (daily habit) +
**crop disease photo diagnosis** (trust & word-of-mouth), Hindi-first, Android-first,
with WhatsApp as a first-class parallel client.

> **Status: Phase 0 — project skeleton.** Local Docker Compose stack, FastAPI backend
> with provider abstraction, Expo app shell. No paid/external services integrated yet.

## Repository Layout

| Path | Purpose |
|---|---|
| `backend/` | Python 3.12 · FastAPI · SQLAlchemy 2 (async) · Alembic · arq workers |
| `mobile/` | React Native · Expo · expo-router · TypeScript (Android-first) |
| `shared/` | Canonical i18n locales + domain data consumed by both apps |
| `infra/` | docker-compose for local dev; AWS ap-south-1 notes for later |
| `docs/` | Setup guide, architecture, ADRs |

## Quick Start (local, no external services needed)

Prereqs: Docker + Docker Compose.

```bash
make up          # postgres + redis + api + worker (runs migrations automatically)
curl localhost:8000/api/v1/health        # liveness
curl localhost:8000/api/v1/health/ready  # db + redis round-trips

make test        # backend pytest inside the container
make down        # stop everything
```

Mobile (separate terminal):

```bash
cd mobile
cp .env.example .env     # point EXPO_PUBLIC_API_URL at your machine/LAN IP
npm install
npm run android          # or: npx expo start
```

## Provider Abstraction

All third-party dependencies sit behind interfaces (`backend/app/providers/base.py`)
and are selected via environment variables — nothing is hardcoded:

| Interface | Env var | V1 default |
|---|---|---|
| VisionProvider (crop diagnosis) | `VISION_PROVIDER` | `null` (safe stub) |
| SMSProvider (OTP) | `SMS_PROVIDER` | `console` |
| WhatsAppClient | `WHATSAPP_PROVIDER` | `null` |
| MandiPriceSource | `MANDI_PRICE_SOURCE` | `stub` |
| ObjectStorage | `STORAGE_PROVIDER` | `local` |

Swapping to OpenAI/Gemini vision, MSG91, WhatsApp Cloud API or S3 later means adding
one adapter class and changing an env var — no business-logic changes.
See `docs/adr/0002-provider-abstraction.md`.

## Docs

- [`docs/SETUP.md`](docs/SETUP.md) — detailed local setup & troubleshooting
- [`docs/architecture.md`](docs/architecture.md) — system design overview
- [`docs/adr/`](docs/adr/) — architecture decision records
- [`AGENTS.md`](AGENTS.md) — conventions for humans and AI agents working in this repo

## Ground Rules

- **Never commit secrets.** `.env` files are gitignored; only `.env.example` is committed.
- AI crop diagnoses are always presented with confidence bands and disclaimers —
  never as guaranteed results (see `docs/adr/0003-diagnosis-uncertainty-audit.md`).
