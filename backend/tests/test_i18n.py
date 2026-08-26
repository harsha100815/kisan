"""Localization tests: fallback chain, missing keys, and language catalogue."""

import json
from pathlib import Path

from app.i18n import loader


def _shared_dir() -> Path:
    # repo_root/shared — tests run from backend/
    return Path(__file__).resolve().parents[2] / "shared"


def test_locale_files_exist_for_v1_languages():
    for code in ("en", "hi"):
        path = _shared_dir() / "i18n" / "locales" / f"{code}.json"
        assert path.exists(), f"missing canonical locale file: {path}"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "diag.disclaimer.not_guaranteed" in _flatten(data)


def _flatten(d: dict, prefix: str = "") -> set[str]:
    keys: set[str] = set()
    for k, v in d.items():
        full = f"{prefix}{k}"
        if isinstance(v, dict):
            keys |= _flatten(v, f"{full}.")
        else:
            keys.add(full)
    return keys


def test_english_and_hindi_have_parity():
    en = _flatten(json.loads((_shared_dir() / "i18n/locales/en.json").read_text("utf-8")))
    hi = _flatten(json.loads((_shared_dir() / "i18n/locales/hi.json").read_text("utf-8")))
    assert en == hi, f"locale drift. only-en: {en - hi} | only-hi: {hi - en}"


def test_t_returns_translation_and_fallback(monkeypatch):
    monkeypatch.setattr(loader, "_shared_locales_dir", lambda: _shared_dir() / "i18n/locales")
    loader.load_locale.cache_clear()

    assert loader.t("diag.disclaimer.not_guaranteed", "en") != ""
    assert loader.t("diag.disclaimer.not_guaranteed", "hi") != "diag.disclaimer.not_guaranteed"
    # Missing language → falls back to English content
    assert loader.t("common.app_name", "xx") == loader.t("common.app_name", "en")
    # Missing key → returns the key itself
    assert loader.t("no.such.key", "en") == "no.such.key"


def test_languages_catalogue_includes_v1_and_is_extensible():
    langs = json.loads((_shared_dir() / "domain/languages.json").read_text("utf-8"))
    codes = {entry["code"] for entry in langs}
    assert {"en", "hi"} <= codes
    # Telugu must be a drop-in addition later (schema supports it now).
    names = {entry["code"]: entry["name"] for entry in langs}
    assert all(isinstance(v, str) and v for v in names.values())
