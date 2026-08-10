"""Local dev helper.

Ensures the backend package is importable regardless of the CWD, then runs
uvicorn or pytest as requested. Keep ZERO logic here — it's just a launcher.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

PY = ROOT / ".venv" / "Scripts" / "python.exe"

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "serve"
    argv = sys.argv[2:]
    if mode == "serve":
        import uvicorn

        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    elif mode == "pytest":
        import pytest

        rc = pytest.main(["-q", *argv])
        sys.exit(rc)
    else:
        raise SystemExit(f"unknown mode: {mode}")
