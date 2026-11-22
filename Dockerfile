# Multi-stage lightweight Dockerfile for Adalat-Pulse
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --timeout 300 --retries 5 -r requirements.txt

# Final Runtime Stage
FROM python:3.11-slim AS runner

WORKDIR /app

# Create non-root system user for security hardening
RUN useradd -u 1001 -m -s /bin/bash adalat_ops && \
    mkdir -p /app/data && \
    chown -R adalat_ops:adalat_ops /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

COPY --chown=adalat_ops:adalat_ops src/ /app/src/

USER adalat_ops

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
