# ADR 0003 — Diagnosis Uncertainty & Audit Trail

Status: accepted · Date: 2026-08-25

## Context

AI crop diagnosis will sometimes be wrong. Presenting it as certain creates
agronomic and trust risks; regulators and partners will ask how decisions were made.

## Decision

- Every response carries `status`, `confidence_band` (`high|medium|low`),
  `is_definitive:false` (by policy, every phase), alternatives, and a localized
  disclaimer key (`diag.disclaimer.not_guaranteed`).
- Every attempt writes one `diagnoses` audit row — including provider crashes —
  storing raw output, model version, latency, and error text.
- Low-confidence or unusable results return `status="unavailable"`; we never guess.

## Consequences

+ Reproducible, reviewable AI behavior; clean labelled data for future fine-tuning.
+ UX copy can never overstate certainty (the API contract enforces it).
− One extra DB write per request (negligible at MVP scale).
