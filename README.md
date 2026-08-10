# ATS Scope — Free Resume ATS Optimizer + Cover Letter Rewriter

A 100% free, no-signup web tool that analyzes how well a resume matches a job
description for ATS (Applicant Tracking System) screening:

1. Upload a resume (PDF/DOCX) and paste a job description
2. Get a **transparent 0-100 ATS compatibility score** with a full component breakdown
3. See **missing keywords with context** — the exact JD sentence, why each matters, and what to do
4. Detect **format issues** that break ATS parsing (tables, columns, images, scanned docs, fonts)
5. Generate **AI-rewritten resume bullets** with a before/after side-by-side diff
6. Generate a **job-synced cover letter** constrained to real resume facts

**Privacy first:** resume files are deleted from the server seconds after
processing. Nothing is stored. No signup, no credit card.

## Positioning

We do **not** claim "ATS auto-rejects 75% of resumes" (that figure is disputed).
We position honestly:

> Fix keyword mismatch + format issues that cause resumes to rank poorly in ATS
> screening — 82% of filtered resumes had <50% keyword match.

## Architecture

```
frontend/   Next.js 14 (App Router) + TypeScript + Tailwind + shadcn/ui
            Framer Motion, react-dropzone, react-diff-viewer-continued, recharts
backend/    Python FastAPI
            pdfplumber + PyMuPDF (PDF), python-docx (DOCX), pytesseract (OCR)
            spaCy (en_core_web_sm) + scikit-learn TF-IDF + sentence-transformers
            (all-MiniLM-L6-v2) for keyword/semantic matching
infra       Supabase (anonymized analytics only) · Upstash Redis (rate limit)
            Vercel (frontend) · Railway (backend)
```

The Next.js dev server proxies `/api/*` to the FastAPI backend
(`frontend/next.config.mjs`), so the preview exposes a single port.

## Project structure

```
.
├── backend/                  # Python FastAPI service
│   ├── app/
│   │   ├── api/routes/       # /scan, /rewrite, /cover-letter endpoints
│   │   ├── core/             # pydantic-settings config (reads .env)
│   │   ├── models/           # Pydantic schemas
│   │   ├── services/
│   │   │   ├── parser/       # PDF (pdfplumber+PyMuPDF), DOCX, OCR
│   │   │   ├── nlp/          # keyword extraction, semantic matching
│   │   │   ├── scoring/      # transparent ATS scorer + format checker
│   │   │   └── ai/           # TokenRouter/Ollama client, rewrite, cover letter
│   │   └── utils/
│   ├── tests/                # pytest suite
│   ├── .env.example          # template — copy to .env
│   ├── requirements.txt
│   └── supabase_schema.sql   # anonymized analytics table
├── frontend/                 # Next.js 14 (App Router, TypeScript, Tailwind)
│   ├── src/
│   │   ├── app/              # layout.tsx, page.tsx, globals.css
│   │   ├── components/       # feature components + shadcn/ui primitives
│   │   └── lib/              # API client, types, utils
│   ├── .env.example          # template — copy to .env.local
│   └── next.config.mjs       # /api/* proxy to the backend
├── docs/DEPLOYMENT.md        # Railway + Vercel + Supabase + Upstash
└── scripts/dev.sh            # runs backend + frontend together
```

## Getting started (local)

### Quick start (both services)
```bash
./scripts/dev.sh
```
Open http://localhost:3000.

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm   # optional but improves keyword extraction
cp .env.example .env                      # set TOKENROUTER_API_KEY if you have one
uvicorn app.main:app --reload --port 8000
```
The `.env` file is loaded automatically (pydantic-settings/python-dotenv); env
vars override it. Health check: http://localhost:8000/health.

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local               # BACKEND_URL=http://localhost:8000
npm run dev
```
Open http://localhost:3000. API calls to `/api/*` are proxied to the backend,
so you only ever talk to the frontend origin.

## AI integration

- **Primary:** TokenRouter (OpenAI-compatible), base URL
  `https://api.tokenrouter.com/v1`, model `moonshotai/kimi-k3-free`, key from
  `TOKENROUTER_API_KEY`
- **Fallback:** local Ollama at `http://localhost:11434/v1`, model
  `qwen2.5-coder:7b` or `llama3.2:3b`, no key needed

If neither is reachable, `/rewrite` and `/cover-letter` return a clear 503.

### Hard rules enforced in every AI call
1. Never invent skills/experience not in the resume
2. Never change numbers/metrics (verified by a deterministic guard after generation)
3. Every change is flagged for the before/after diff
4. Resume is the only allowed source of facts

## Scoring (fully transparent)

Overall = weighted average of four explained components:

| Component | Weight | What it measures |
|---|---|---|
| Keyword match | 40% | share of JD keywords found in the resume (exact + semantic) |
| Format compatibility | 30% | tables, columns, images, scanned docs, fonts, contact info |
| Section coverage | 15% | summary, experience, education, skills sections present |
| Content quality | 15% | quantified outcomes, action verbs, length balance |

Every deduction maps to concrete evidence shown in the UI (exact JD sentence,
detected issue, suggested fix).

## Getting started (local)

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm   # optional but improves keyword extraction
cp .env.example .env                      # set TOKENROUTER_API_KEY if you have one
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local               # BACKEND_URL=http://localhost:8000
npm run dev
```
Open http://localhost:3000. API calls to `/api/*` are proxied to the backend.

### Tests
```bash
cd backend && python -m pytest tests -q
cd frontend && npx tsc --noEmit && npm run build
```

## Privacy & abuse controls

- Uploads go to a throwaway per-request temp dir and are deleted in a `finally`
  block immediately after parsing (`backend/app/services/temp_files.py`)
- A background sweeper removes orphaned files from crashed workers
- Rate limiting: **5 scans / IP / day** (Upstash Redis, in-memory fallback),
  separate quota for AI calls — keys are hashed, never stored raw
- Supabase analytics receive only aggregate scores/counts, never content

See `docs/DEPLOYMENT.md` for Railway + Vercel + Supabase + Upstash setup.
