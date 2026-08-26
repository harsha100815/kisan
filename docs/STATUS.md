# Project Status Report — Kisan Sahayak

**Date:** 2026-08-26 · **Phase:** 0 (skeleton) · **Repo:** https://github.com/harsha100815/kisan (`main` @ `6cd1abd`)

---

## 1. What this project is

An agri-tech MVP for Indian smallholder farmers with two core features:

1. **Daily mandi prices** — the daily-habit hook
2. **Crop disease photo diagnosis** — AI vision that builds trust via word-of-mouth

Hindi-first, Android-first, low-end-device friendly. WhatsApp planned as a parallel client.

## 2. What exists right now

| Area | State |
|---|---|
| Local dev stack | ✅ Working (Docker Compose: postgres + redis + api + worker) |
| Backend API | ✅ Working, tested (12/12), lint clean |
| Database | ✅ Migrated (`users`, `diagnoses` tables) |
| Mobile app | ⚠️ Shell only — deps not installed, never run |
| WhatsApp client | ❌ Not started (provider slot stubbed) |
| Real providers | ❌ All stubs (vision, SMS, mandi data, storage) |

## 3. What's verified working

All of this was confirmed live on 2026-08-26:

- `GET /api/v1/health` → ok; `GET /api/v1/health/ready` → postgres + redis round-trips pass
- Alembic migration applied; tables exist
- `POST /api/v1/diagnosis/diagnose` end-to-end: upload image → contract response
  (`status: unavailable`, `is_definitive: false`, disclaimer key present) and an
  **audit row persisted in Postgres**
- `GET /api/v1/diagnosis/disclaimer?language=hi|en` returns localized disclaimers
- `make test` → 12 passed · `make lint` → all checks passed

## 4. Recently fixed (this session)

1. **Test bug:** `test_low_confidence_is_banded_not_definitive` passed `None` as the DB
   session → crash. Now uses a real session from `db_sessionmaker`.
2. **Lint debt:** 17 ruff errors cleared (import sorting, `X | Y` annotations,
   line-length rewraps).
3. **Repo setup:** project now has its own git repo (was previously swallowed by a
   home-directory repo) with a secrets-audited initial commit pushed to GitHub.
   `.env` files containing real keys are properly gitignored.

## 5. Architecture in one paragraph

Monorepo. The backend (`backend/`, Python 3.12 + FastAPI + SQLAlchemy 2 async +
Alembic + arq) exposes everything under `/api/v1`. Every external dependency sits
behind a **provider interface** (`app/providers/base.py`) chosen by env var — today
they're safe stubs; swapping in OpenAI vision, MSG91 SMS, WhatsApp Cloud API or S3
later means adding one adapter class + one env var, no business-logic changes.
The mobile app (`mobile/`, Expo + expo-router + TypeScript strict) is Android-first.
Shared copy/data lives in `shared/` (i18n locales `hi.json`/`en.json`, domain data)
and is consumed by both clients. Design decisions are recorded as ADRs in `docs/adr/`.

Key API surface today:

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/health` | liveness |
| `GET /api/v1/health/ready` | db + redis readiness |
| `POST /api/v1/diagnosis/diagnose` | photo diagnosis (contract enforces uncertainty + audit row on every call) |
| `GET /api/v1/diagnosis/disclaimer` | localized disclaimer text |

## 6. How to run it

Prereqs: Docker Desktop.

```bash
cd agri-test
make up                      # start postgres + redis + api + worker (auto-migrates)
curl localhost:8000/api/v1/health

make test                    # pytest inside container
make lint                    # ruff check + format check
make down                    # stop stack
```

Mobile (once dependencies get installed):

```bash
cd mobile
npm install
cp .env.example .env         # point EXPO_PUBLIC_API_URL at your LAN IP
npx expo start               # then scan QR with Expo Go (Android)
```

## 7. Rules every contributor must follow

From `AGENTS.md` — the non-negotiables:

- **Secrets never enter git.** Real keys only in local `.env` (gitignored); new config
  goes into `app/core/config.py` + `.env.example` together.
- **No hardcoded user-facing strings** — everything through i18n locale keys.
- **External services only behind provider interfaces**, selected by env var.
- **AI diagnoses are never definitive**: always confidence band + `is_definitive: false`
  + disclaimer + audit row per call.
- **Android-first mobile**, theme tokens for colors/spacing.
- Conventional commits (`feat(api): …`), small PRs, CI green before merge.
- **Phase discipline:** Phase 0 = skeleton. Don't smuggle Phase 1 features
  (auth, ingestion pipeline, full diagnosis flow) into unrelated changes.

## 8. Roadmap from here

Phase 1 candidates, roughly in suggested order:

1. **Run the mobile shell** — install deps, boot in Expo Go, wire home screen to `/health`
2. **Real mandi price endpoint** (data.gov.in provider behind existing interface)
3. **Phone auth via OTP** (MSG91 console provider already sketched)
4. **Wire a real vision provider** for diagnosis (OpenAI adapter pattern ready)
5. **WhatsApp Cloud API client** as parallel surface
6. CI pipeline (ruff + pytest + tsc + eslint) — config folder `.github/` exists but workflow unverified
