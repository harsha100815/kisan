# AGENTS.md — Conventions for Humans & AI Agents

Working agreements for anyone (or any agent) modifying this repository.

## Commands

```bash
make up            # start full local stack (db, redis, api, worker)
make logs          # tail api logs
make migrate       # run alembic migrations against the running db
make test          # backend tests (inside container)
make lint          # ruff check + format check
make down          # stop stack
make clean         # also remove volumes (destroys local data)
```

Backend one-offs:

```bash
docker compose -f infra/docker-compose.yml exec api bash
docker compose -f infra/docker-compose.yml exec api alembic revision --autogenerate -m "..."
```

## Non-negotiable Rules

1. **Secrets never enter git.** Real keys live only in local `.env` files (gitignored).
   New config goes into `app/core/config.py` + `.env.example` together.
2. **No user-facing strings hardcoded in code.** All copy lives in
   `shared/i18n/locales/{lang}.json`; reference it by key. English + Hindi are V1;
   the schema must allow dropping in `te.json` etc. without code changes.
3. **External services stay behind provider interfaces** (`app/providers/base.py`).
   Business logic imports Protocols from there, never SDK clients directly.
4. **AI diagnoses are never definitive.** Every response carries a confidence band,
   `is_definitive: false`, and a disclaimer key. Every call writes an audit row.
5. **Android-first mobile.** Test on low-end Android assumptions; min font sizes from
   `theme/tokens.ts`; no iOS-specific APIs without an Android-safe fallback.

## Code Style

- Backend: Python 3.12, async everywhere, SQLAlchemy 2.0 typed style, Pydantic v2
  settings/schemas, ruff for lint+format. Type hints required on all public functions.
- Migrations: Alembic only; never `Base.metadata.create_all` outside tests;
  every schema change ships with a migration before code depending on it merges.
- Mobile: TypeScript strict; expo-router file conventions; server state via the typed
  API client in `src/api/`; no inline magic colors/spacing — use theme tokens.
- Tests: every bug fix adds a regression test; provider adapters get contract tests
  with mocked transports, not live network calls.

## Commit / PR Discipline

- Conventional commits: `feat(api): ...`, `fix(mobile): ...`, `chore(infra): ...`
- Small PRs; CI green (ruff, pytest, tsc, eslint) before merge.
- Do not commit generated artifacts (`node_modules`, `.expo`, `__pycache__`, `data/`).

## Phase Discipline

Phase 0 = skeleton only. Don't pull Phase 1 features (auth, ingestion pipeline,
full diagnosis flow) into unrelated changes. Deferred features are listed in
`docs/architecture.md`.
