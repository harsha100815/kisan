# Mobile App (Expo)

Android-first React Native shell. Phase 0 contains only: language selection,
bottom-tab navigation, i18n wiring, theme tokens, and a typed API client stub.

## Run

```bash
cp .env.example .env      # set EXPO_PUBLIC_API_URL (see note below)
npm install
npx expo start            # then press 'a' for Android emulator
```

**API URL notes**
- Android emulator → `http://10.0.2.2:8000/api/v1` (host loopback)
- Physical device → your machine's LAN IP, e.g. `http://192.168.1.5:8000/api/v1`
- Start the backend first: `make up` from the repo root.

## Conventions

- File-based routing via expo-router; screens under `src/app`.
- All user-facing strings come from `src/i18n` (canonical files in `../../shared/i18n/locales`).
  Adding Telugu later = add `te.json` + register it in `SUPPORTED_LANGUAGES`.
- No hardcoded colors/spacing — use `src/theme/tokens.ts`.
- TypeScript strict mode must pass: `npm run typecheck`.
