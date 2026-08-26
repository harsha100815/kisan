/**
 * i18n for the mobile app.
 * Canonical strings live in shared/i18n/locales; Metro resolves ../../shared via
 * the mobile/package.json "workspaces" hack-free watchFolders config in metro.config.js.
 */
import en from '../../shared/i18n/locales/en.json';
import hi from '../../shared/i18n/locales/hi.json';
import { createContext, useContext } from 'react';

export type LanguageCode = 'en' | 'hi';

export const dictionaries: Record<LanguageCode, Record<string, unknown>> = { en, hi };

export const SUPPORTED_LANGUAGES: { code: LanguageCode; nativeName: string }[] = [
  { code: 'hi', nativeName: 'हिंदी' },
  { code: 'en', nativeName: 'English' },
];

type TFunc = (key: string) => string;

function resolve(dict: Record<string, unknown>, key: string): string | undefined {
  const value = key.split('.').reduce<unknown>(
    (acc, part) => (acc && typeof acc === 'object' ? (acc as Record<string, unknown>)[part] : undefined),
    dict,
  );
  return typeof value === 'string' ? value : undefined;
}

export function makeT(lang: LanguageCode): TFunc {
  return (key: string) => resolve(dictionaries[lang], key) ?? resolve(dictionaries.en, key) ?? key;
}

export const LanguageContext = createContext<{ lang: LanguageCode; setLang: (l: LanguageCode) => void }>({
  lang: 'hi',
  setLang: () => undefined,
});

export const useLanguage = () => useContext(LanguageContext);
export const useT = (): TFunc => makeT(useLanguage().lang);
