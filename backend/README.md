---
title: ATS Scope Backend
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# ATS Scope — Backend API

A FastAPI service that analyzes a job seeker's resume against a job description and returns an ATS-style compatibility breakdown: keyword match scores, missing-keywords report, format issue warnings, before/after bullet rewrites, and a tailored cover letter. Includes privacy-first file handling (uploads are deleted immediately after parsing), per-IP rate limiting, and graceful degradation when the optional AI provider is not configured.

## Endpoints

* `GET /health` — liveness probe
* `POST /analyze` — accept a resume (PDF/DOCX) + JD text, return score + missing keywords + format issues
* `POST /rewrite` — AI-powered bullet-point rewriting given a JD
* `POST /cover-letter` — AI-powered cover letter generation
* `GET /docs` — interactive OpenAPI docs

## Environment Secrets (set in HF Spaces → Settings → Secrets)

* `TOKENROUTER_API_KEY` — required for /rewrite and /cover-letter (leave blank to disable AI features)
* `TOKENROUTER_BASE_URL` (default `https://api.tokenrouter.com/v1`)
* `TOKENROUTER_MODEL` (default `moonshotai/kimi-k3-free`)
* `UPSTASH_REDIS_REST_URL` + `UPSTASH_REDIS_REST_TOKEN` — optional; without these, in-memory rate limiting is used
* `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` — optional anonymous analytics
* `CORS_ORIGINS` — JSON list of allowed origins, e.g. `["https://your-vercel-app.vercel.app"]`
* `RATE_LIMIT_PER_DAY` (default `5`)
* `TEMP_DIR` (default `/tmp/ats_optimizer`)

The container listens on port `7860` (overridable via `PORT`).
