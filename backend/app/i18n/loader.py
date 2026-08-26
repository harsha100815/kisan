"""Localization loader for the backend.

Reads the canonical locale files from /shared/i18n/locales (mounted read-only in
docker; override with SHARED_DIR when running on host). English is the fallback
language: a missing key in `hi` resolves to `en`, and a missing language falls
back to `en` entirely. See docs/adr/0004-localization-strategy.md.
"""

import json
import logging
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

FALLBACK_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ("en", "hi")


def _shared_locales_dir() -> Path:
    return Path("/shared/i18n/locales")


@lru_cache
def load_locale(lang: str) -> dict:
    path = _shared_locales_dir() / f"{lang}.json"
    if not path.exists():
        logger.warning("locale file missing for %s, falling back to %s", lang, FALLBACK_LANGUAGE)
        lang = FALLBACK_LANGUAGE
        path = _shared_locales_dir() / f"{lang}.json"
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def t(key: str, lang: str = FALLBACK_LANGUAGE, **kwargs: object) -> str:
    """Translate a dotted key like 'diag.disclaimer.not_guaranteed'.

    Resolution order: requested language → fallback language → key itself.
    """
    value: object = load_locale(lang)
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            break
        value = value[part]
    else:
        text = str(value)
        return text.format(**kwargs) if kwargs else text

    if lang != FALLBACK_LANGUAGE:
        return t(key, FALLBACK_LANGUAGE, **kwargs)
    logger.warning("missing i18n key: %s", key)
    return key


def supported_languages() -> list[dict[str, str]]:
    """From shared/domain/languages.json — the single source of truth."""
    path = Path("/shared/domain/languages.json")
    if path.exists():
        with open(path, encoding="utf-8") as fh:
            return list(json.load(fh))
    return [{"code": code} for code in SUPPORTED_LANGUAGES]
