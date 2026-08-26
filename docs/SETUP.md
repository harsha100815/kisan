# Setup Guide

## Prerequisites

- Docker Desktop (or Engine) with Compose v2+
- Node 20+ and npm (mobile development only)
- No cloud accounts, API keys, or paid services required for Phase 0.

## 1. Start the backend stack

From the repo root:

```bash
cp backend/.env.example backend/.env   # defaults work locally; no keys needed
make up
```

This starts:

| Service | URL/Port |
|---|---|
| FastAPI | http://localhost:8000 |
| Swagger docs | http://localhost:8000/docs |
| Postgres | localhost:5432 (user/pass/db: `kisan`) |
| Redis | localhost:6379 |

Migrations run automatically via the one-shot `migrate` container.

## 2. Verify

```bash
curl localhost:8000/api/v1/health
# {"status":"ok",...}

curl localhost:8000/api/v1/health/ready
# {"ready":true,"checks":[{"component":"postgres","ok":true},{"component":"redis","ok":true}]}

# Diagnosis contract with the null provider:
curl -s -X POST localhost:8000/api/v1/diagnosis/diagnose \
  -F "image=@some-leaf.jpg" -F "crop_key=cotton" | python3 -m json.tool
# Expect: "status": "unavailable", "is_definitive": false, disclaimer_key present

make test        # pytest inside the container
docker compose -f infra/docker-compose.yml logs worker   # worker startup line
```

## 3. Run the mobile app

```bash
cd mobile
cp .env.example .env
npm install
npx expo start --android   # Android emulator; see mobile/README.md for device URLs
```

The language screen appears first; choosing a language opens the four tabs.
All screens are placeholders in Phase 0.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Port 8000/5432/6379 busy | Stop the conflicting service or change the host port mapping in `infra/docker-compose.yml`. |
| `health/ready` shows postgres down | Wait for the healthcheck (`pg_isready`); check `docker compose -f infra/docker-compose.yml logs postgres`. |
| Emulator can't reach API | Use `10.0.2.2` (not `localhost`) in `mobile/.env`; physical devices need your LAN IP. |
| Metro can't find shared locales | Ensure `metro.config.js` watchFolders includes `../shared`; run `npx expo start -c`. |

## Reset everything

```bash
make clean   # stops stack AND deletes the postgres volume
```
