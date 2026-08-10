import type {
  AnalyzeResponse,
  CoverLetterResponse,
  RewriteRequest,
  RewriteResponse,
} from "./types";

const BASE = "/api"; // rewritten by Next.js to the FastAPI backend

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

async function parseError(res: Response): Promise<ApiError> {
  let detail = `Request failed with status ${res.status}.`;
  try {
    const body = await res.json();
    if (typeof body?.detail === "string") detail = body.detail;
    else if (typeof body?.error === "string") detail = body.error;
  } catch {
    /* non-JSON error body */
  }
  return new ApiError(res.status, detail);
}

export async function scanResume(
  file: File,
  jd: string,
): Promise<{ data: AnalyzeResponse; remaining: number | null }> {
  const form = new FormData();
  form.append("file", file);
  form.append("jd", jd);

  const res = await fetch(`${BASE}/analyze`, { method: "POST", body: form });
  if (!res.ok) throw await parseError(res);

  const remainingRaw = res.headers.get("X-RateLimit-Remaining");
  const remaining = remainingRaw ? Number(remainingRaw) : null;
  return { data: (await res.json()) as AnalyzeResponse, remaining };
}

export async function rewriteBullets(
  req: RewriteRequest,
): Promise<RewriteResponse> {
  const res = await fetch(`${BASE}/rewrite`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw await parseError(res);
  return (await res.json()) as RewriteResponse;
}

export async function generateCoverLetter(payload: {
  jd: string;
  resume_summary: string;
  company: string;
  role: string;
}): Promise<CoverLetterResponse> {
  const res = await fetch(`${BASE}/cover-letter`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw await parseError(res);
  return (await res.json()) as CoverLetterResponse;
}
