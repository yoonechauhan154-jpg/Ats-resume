FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    # Default port Hugging Face Spaces expects for Docker SDK
    PORT=7860 \
    # Writable temp dir — the default /tmp works inside Docker, but we surface
    # it as a build-time env so it can be overridden if the runtime makes /tmp read-only.
    TEMP_DIR=/tmp/ats_optimizer

# Non-root user — HF Spaces runs containers as uid 1000 by convention
RUN useradd -m -u 1000 atsuser

WORKDIR /app

# System deps for pdfplumber / OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
        tesseract-ocr \
        tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

# spaCy English model (kept in the image so scoring works offline)
RUN python -m spacy download en_core_web_sm || true

COPY app ./app

# Ensure temp dir exists and is writable by the runtime user
RUN mkdir -p ${TEMP_DIR} && chown -R atsuser:atsuser ${TEMP_DIR} /app

USER atsuser

# HF Spaces route traffic to :7860 by default; honor $PORT if overridden.
EXPOSE 7860
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
