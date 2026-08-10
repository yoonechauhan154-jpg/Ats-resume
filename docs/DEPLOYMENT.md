# Deployment

Free-tier stack: Vercel (frontend) + Railway (backend) + Supabase (analytics)
+ Upstash (rate limiting). No resume content is ever stored anywhere.

## 1. Backend on Railway

1. Create a new Railway service from the `backend/` directory (Dockerfile included).
2. Set the environment variables (from `backend/.env.example`):
   - `TOKENROUTER_API_KEY` (optional — without it AI endpoints need a reachable Ollama)
   - `REDIS_URL` (Upstash)
   - `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` (optional)
   - `RATE_LIMIT_PER_DAY=5`
   - `CORS_ORIGINS=https://<your-app>.vercel.app,https://*.monkeycode-ai.live`
3. Note the public URL, e.g. `https://ats-api.up.railway.app`.

Optional: install the spaCy model inside the image for richer keyword extraction
(the Dockerfile already attempts `python -m spacy download en_core_web_sm`).

## 2. Upstash Redis

1. Create a free Redis database at https://console.upstash.com.
2. Copy the `REDIS_URL` into the backend env. Without it, the backend uses an
   in-memory limiter (fine for one instance).

## 3. Supabase (anonymized analytics only)

1. Create a free Supabase project.
2. Run `backend/supabase_schema.sql` in the SQL editor to create the `analytics` table.
3. Set `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` on the backend.
4. Only aggregate numbers are sent (score, component scores, counts). Never
   resume text, JD text, or keywords.

## 4. Frontend on Vercel

1. Import the `frontend/` directory as a new project.
2. Add the environment variable `BACKEND_URL=https://ats-api.up.railway.app`.
3. The app uses a Next.js rewrite: `/api/:path*` → `BACKEND_URL/:path*`. No CORS
   headaches, single exposed origin.
4. Deploy. The `experimental.allowedHosts` in `next.config.mjs` already permits
   the `*.monkeycode-ai.live` preview domain.

## 5. Ollama fallback (self-hosted)

To enable the AI fallback, run Ollama somewhere reachable by the backend and set:

```
OLLAMA_BASE_URL=http://<host>:11434/v1
OLLAMA_MODEL=qwen2.5-coder:7b
```

No API key required. `llama3.2:3b` is a lighter alternative.
