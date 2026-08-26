# ADR 0001 — Monorepo Layout & Worker Placement

Status: accepted · Date: 2026-08-25

## Context

We need mobile, API, background workers, shared localization assets, and infra in
one repository with one CI pipeline, without duplicating models/config between
API and worker packages.

## Decision

- Top-level: `mobile/`, `backend/`, `shared/`, `infra/`, `docs/`.
- **Workers live inside the backend** (`backend/app/workers/`) rather than a
  top-level `workers/` package. One Docker image; container command selects the
  role (`uvicorn` vs `arq`).
- `shared/i18n/locales` is canonical for UI strings; Metro `watchFolders` exposes
  it to the app and a volume mount exposes it read-only to backend containers.

## Consequences

+ No model/config duplication; single migration history.
+ One CI setup per stack, path-filtered.
− Slightly larger backend image for workers (acceptable at MVP scale).
