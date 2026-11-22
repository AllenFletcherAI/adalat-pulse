# Production Dockerfile for Adalat-Pulse Gateway
FROM python:3.11-slim

WORKDIR /app

# Create non-root system user for security hardening
RUN useradd -u 1001 -m -s /bin/bash adalat_ops && \
    mkdir -p /app/data && \
    chown -R adalat_ops:adalat_ops /app

# Install pre-packaged binary wheels with zero network latency
COPY .docker_wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*.whl && \
    rm -rf /wheels

ENV PYTHONUNBUFFERED=1

COPY --chown=adalat_ops:adalat_ops src/ /app/src/

USER adalat_ops

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
