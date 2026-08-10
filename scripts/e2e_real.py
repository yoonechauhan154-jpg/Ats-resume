"""End-to-end REAL network test against a live backend.

Spin up the backend (fresh, picking up the current .env), then:
  1. /analyze  -> parse test-data/sample_resume.pdf against a real JD
  2. /rewrite  -> rewrite parsed bullets (uses TokenRouter in real-network mode)
  3. /cover-letter -> generate a cover letter

Ollama is intentionally broken in .env so any non-error AI reply MUST come from
TokenRouter (the fallback can never succeed). Model used is printed so you can
see exactly which provider responded.

Usage:
    python scripts/e2e_real.py                 # spin up temp server, run, shut down
    python scripts/e2e_real.py --running       # assume server already on :8000
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
BACKEND = HERE.parent / "backend"
BASE = "http://127.0.0.1:8000"
RESUME_PDF = HERE.parent / "test-data" / "sample_resume.pdf"

JD = """Senior Backend Engineer (Python / FastAPI)

Acme Corp is hiring a Senior Backend Engineer to own high-throughput services.

Responsibilities:
- Design and build REST APIs in Python using FastAPI and PostgreSQL
- Write clean, tested, well-documented code and lead code reviews
- Deploy to AWS with Docker and CI/CD
- Mentor engineers and drive architectural decisions
- Improve observability (metrics, tracing, logging)

Requirements:
- 5+ years Python backend experience
- FastAPI (or similar), async programming
- PostgreSQL / SQL, Redis, message queues
- AWS, Docker, CI/CD
- Strong written communication
"""


def _post_json(path: str, payload: dict, timeout: float = 120.0) -> tuple[int, dict, float]:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        BASE + path, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode()), time.perf_counter() - t0
    except urllib.error.HTTPError as e:
        try:
            detail = json.loads(e.read().decode())
        except Exception:
            detail = {"detail": str(e)}
        return e.code, detail, time.perf_counter() - t0


def _post_multipart(path: str, file_path: Path, field_name: str, form: dict, timeout=120.0):
    boundary = "----e2eBoundary"
    parts = []
    for k, v in form.items():
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
        )
    data = file_path.read_bytes()
    parts.append(
        (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{field_name}\"; "
            f"filename=\"{file_path.name}\"\r\nContent-Type: application/pdf\r\n\r\n"
        ).encode()
        + data
        + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)
    req = urllib.request.Request(
        BASE + path,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode()), time.perf_counter() - t0
    except urllib.error.HTTPError as e:
        try:
            detail = json.loads(e.read().decode())
        except Exception:
            detail = {"detail": str(e)}
        return e.code, detail, time.perf_counter() - t0


def _server_up() -> bool:
    """Server counts as up if /analyze responds (any non-connection error)."""
    try:
        _post_json("/analyze", {}, timeout=5)
        return True
    except urllib.error.URLError:
        return False
    except Exception:
        return True


def _start_server() -> subprocess.Popen:
    py = BACKEND / ".venv" / "Scripts" / "python.exe"
    if not py.exists():
        py = Path(sys.executable)
    proc = subprocess.Popen(
        [str(py), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(BACKEND),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(60):
        if proc.poll() is not None:
            raise RuntimeError("server exited immediately; check venv / uvicorn install")
        if _server_up():
            return proc
        time.sleep(0.5)
    raise RuntimeError("server did not start within 30s")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--running", action="store_true", help="use an already-running :8000 server")
    args = ap.parse_args()

    proc = None
    if args.running:
        if not _server_up():
            print("!! expected a server on :8000 but can't reach it", file=sys.stderr)
            return 2
    else:
        print("== starting fresh backend (current .env: real TokenRouter key, BROKEN Ollama) ==")
        proc = _start_server()
        print("== server up ==\n")

    try:
        print("TEST 1: POST /analyze (sample_resume.pdf + real JD) ...")
        st, scan, dt = _post_multipart(
            "/analyze", RESUME_PDF, "file", {"jd": JD}
        )
        print(f"    status={st}  time={dt:.2f}s")
        if st != 200:
            print(f"    ERROR: {json.dumps(scan)[:500]}")
            return 1
        overall = scan.get("score", {}).get("overall")
        bullets = scan.get("resume_bullets") or []
        resume_text = scan.get("resume_text") or ""
        present = scan.get("present_keywords") or []
        missing = scan.get("missing_keywords") or []
        print(f"    overall score     : {overall}")
        print(f"    resume word count : {scan.get('resume_word_count')}")
        print(f"    jd word count     : {scan.get('jd_word_count')}")
        print(f"    present keywords  : {len(present)}  -> {present[:8]}")
        print(f"    missing keywords  : {len(missing)}  -> "
              f"{[m.get('keyword') for m in missing[:8]]}")
        print(f"    format issues     : {[i.get('type') for i in (scan.get('format_issues') or [])]}")
        print(f"    sections          : "
              f"{[(s.get('name'), s.get('present')) for s in (scan.get('sections') or [])]}")
        print(f"    bullets parsed    : {len(bullets)}")

        # Keep the AI request small enough to stay within 5/day rate limit but
        # big enough to be meaningful.
        use_bullets = bullets[:3] if bullets else [
            "Developed backend APIs in Python serving 1M requests/day",
            "Led migration to FastAPI, reducing latency by 40%",
            "Wrote unit tests raising coverage from 60% to 95%",
        ]
        context = resume_text[:2000]

        print("\nTEST 2: POST /rewrite (real network via TokenRouter; Ollama broken) ...")
        st, rw, dt = _post_json(
            "/rewrite",
            {"bullets": use_bullets, "jd": JD, "role": "Senior Backend Engineer", "context": context},
            timeout=180,
        )
        print(f"    status={st}  time={dt:.2f}s")
        if st != 200:
            print(f"    FAILED (good-faith attempt made): {json.dumps(rw)[:800]}")
            rewrite_ok = False
        else:
            rewrite_ok = True
            print(f"    model_used        : {rw.get('model_used')}")
            print(f"    rules_applied     : {rw.get('rules_applied')}")
            for r in (rw.get("rewritten") or [])[:3]:
                print(f"\n    ORIGINAL : {r.get('original')}")
                print(f"    REWRITTEN: {r.get('rewritten')}")
                print(f"    changed  : {r.get('changed')}")
                print(f"    preserved: {r.get('preserved')}")
                print(f"    reason   : {r.get('reason')}")

        print("\nTEST 3: POST /cover-letter (real network via TokenRouter; Ollama broken) ...")
        st, cl, dt = _post_json(
            "/cover-letter",
            {
                "jd": JD,
                "resume_summary": context,
                "company": "Acme Corp",
                "role": "Senior Backend Engineer",
                "tone": "professional",
                "max_length_words": 250,
            },
            timeout=180,
        )
        print(f"    status={st}  time={dt:.2f}s")
        if st != 200:
            print(f"    FAILED (good-faith attempt made): {json.dumps(cl)[:800]}")
            cl_ok = False
        else:
            cl_ok = True
            print(f"    model_used        : {cl.get('model_used')}")
            print(f"    warning           : {cl.get('warning')}")
            txt = (cl.get("cover_letter") or "").strip()
            print(f"    word count        : {len(txt.split())}")
            print("    ---- cover letter start ----")
            print("    " + txt.replace("\n", "\n    "))
            print("    ---- cover letter end ----")

        print("\n" + "=" * 60)
        print(f"SUMMARY  rewrite={'OK' if rewrite_ok else 'FAIL'}  cover_letter={'OK' if cl_ok else 'FAIL'}")
        return 0 if (rewrite_ok and cl_ok) else 1
    finally:
        if proc is not None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
            print("== test server shut down ==")


if __name__ == "__main__":
    sys.exit(main())
