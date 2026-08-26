# AWS ap-south-1 (Mumbai) — Deployment Notes (Placeholder)

Phase 0 runs everything locally via `infra/docker-compose.yml`. This file records
the intended production path **without provisioning anything yet**.

## Intended target architecture

| Concern | Plan |
|---|---|
| Region | ap-south-1 (Mumbai) — DPDP-aligned data residency |
| API | ECS Fargate service, image from `backend/Dockerfile`, command `uvicorn` |
| Workers | Same image, command `arq app.workers.runner.WorkerSettings` |
| Database | RDS PostgreSQL 16, Multi-AZ later; single instance for MVP |
| Cache/queue | ElastiCache Redis (or Upstash during earliest MVP) |
| Images | S3 bucket + CloudFront OAC; presigned upload URLs |
| Secrets | AWS Secrets Manager / SSM Parameter Store — never baked into images |
| CI/CD | GitHub Actions → ECR → ECS deploy (added only when we get here) |
| Edge | Cloudflare DNS/WAF in front of ALB |

## Migration sketch (when approved)

1. `terraform` or `cdk` in this folder, one environment (`staging`) first.
2. Move compose env vars into SSM; keep identical variable names so
   `app/core/config.py` does not change.
3. Add `infra/aws/` deploy workflow guarded by manual approval.

## Explicitly NOT done in Phase 0

No IaC, no cloud accounts touched, no images pushed anywhere.
