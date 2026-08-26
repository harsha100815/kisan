# ADR 0004 — Localization Strategy

Status: accepted · Date: 2026-08-25

## Context

V1 ships English + Hindi; Telugu/Marathi etc. follow within months. Strings must
never be hardcoded on either client or server.

## Decision

Canonical locale files: `shared/i18n/locales/{lang}.json`. Resolution order:
requested language → English → key itself. The language catalogue
(`shared/domain/languages.json`) drives pickers on both sides. Adding a language =
one JSON file + one catalogue entry + translations; no code changes.

## Consequences

+ Product can add languages without engineering involvement (beyond review).
+ Parity test (`backend/tests/test_i18n.py`) prevents silent key drift between languages.
− Backend depends on a mounted `/shared` path in containers (documented in SETUP.md).
