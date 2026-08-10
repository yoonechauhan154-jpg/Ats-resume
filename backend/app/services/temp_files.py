"""Secure temp-file handling.

Files are written to a per-request directory under the configured temp dir,
used once, and *always* removed afterwards (even on exceptions). A background
sweeper removes any orphaned files left by crashed workers.

Privacy: no resume content is ever written outside this directory and it is
deleted immediately after processing.
"""

from __future__ import annotations

import logging
import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Iterator

from ..core.config import get_settings

logger = logging.getLogger(__name__)

_MAX_ORPHAN_AGE_SECONDS = 60 * 60 * 2  # sweep files older than 2h


def ensure_temp_root() -> Path:
    """Make sure the configured temp dir exists and is writable.

    If the configured path is on a read-only filesystem (some hosted
    environments do this), fall back to a well-known writable location so the
    app doesn't crash on startup.
    """
    settings = get_settings()
    candidates = [
        Path(settings.temp_dir),
        Path(f"/tmp/{Path(settings.temp_dir).name or 'ats_optimizer'}"),
        Path(".ats-tmp").resolve(),
    ]
    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            test_file = candidate / f".write-test-{uuid.uuid4().hex[:8]}"
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink()
            if candidate != Path(settings.temp_dir):
                logger.warning(
                    "temp_dir=%s is not writable; fell back to %s",
                    settings.temp_dir,
                    candidate,
                )
            return candidate
        except OSError as exc:
            logger.warning("temp_root candidate %s not writable: %s", candidate, exc)
    # Last resort — inside the project directory
    fallback = Path.cwd() / ".ats-tmp"
    fallback.mkdir(parents=True, exist_ok=True)
    logger.warning("All configured temp paths failed; using %s", fallback)
    return fallback


def sweep_orphans() -> int:
    """Remove abandoned request dirs (left by a crashed process)."""
    root = ensure_temp_root()
    now = time.time()
    removed = 0
    for entry in root.iterdir():
        if not entry.is_dir():
            continue
        try:
            if now - entry.stat().st_mtime > _MAX_ORPHAN_AGE_SECONDS:
                shutil.rmtree(entry, ignore_errors=True)
                removed += 1
        except OSError:
            continue
    return removed


def make_request_dir() -> Path:
    """Create a fresh, unpredictable directory for one request's files."""
    root = ensure_temp_root()
    req_dir = root / uuid.uuid4().hex
    req_dir.mkdir(parents=True, exist_ok=False)
    return req_dir


def write_upload(request_dir: Path, filename: str, data: bytes) -> Path:
    """Write an upload with a sanitized name. Rejects path traversal."""
    safe = os.path.basename(filename.replace("\\", "/"))
    if not safe:
        raise ValueError("empty filename")
    dest = request_dir / safe
    dest.write_bytes(data)
    return dest


def delete_request_dir(request_dir: Path) -> None:
    """Hard-delete a request dir and everything inside it."""
    shutil.rmtree(request_dir, ignore_errors=True)


def cleanup_after(func):
    """Decorator: delete the request dir after `func` returns or raises."""

    def wrapper(*args, **kwargs):
        request_dir: Path = kwargs.get("request_dir")  # type: ignore[assignment]
        if request_dir is None and args:
            candidate = args[-1]
            if isinstance(candidate, Path):
                request_dir = candidate
        try:
            return func(*args, **kwargs)
        finally:
            if request_dir is not None:
                delete_request_dir(request_dir)

    return wrapper
