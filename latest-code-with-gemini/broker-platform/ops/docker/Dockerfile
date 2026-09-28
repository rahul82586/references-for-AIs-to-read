# syntax=docker/dockerfile:1
# ============================================================================
# Broker Platform API — multi-stage, non-root (M5).
#
#   docker build -f ops/docker/Dockerfile -t broker-platform-api .
#
# Runtime needs neither the development surface (grpcio, pandas, clickhouse,
# kafka, locust) nor the test extras — see ops/docker/requirements-runtime.txt.
# Secrets come from the environment (compose `env_file:` / orchestrator), never
# from the image: api.main refuses to boot without SECRET_KEY + ADMIN_API_KEY.
# ============================================================================

# ---- builder: wheels into a venv -------------------------------------------
FROM python:3.11-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
COPY ops/docker/requirements-runtime.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install -r requirements-runtime.txt

# ---- runtime: slim, non-root ------------------------------------------------
FROM python:3.11-slim AS runtime

RUN useradd --uid 10001 --create-home --shell /usr/sbin/nologin broker

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY . /app
RUN chown -R broker:broker /app

USER broker
EXPOSE 8000

# No curl in slim: probe /health with the interpreter that is already there.
# A degraded server (DB or Redis down) returns 503 and fails the healthcheck,
# which is what lets compose/Kubernetes act on it.
HEALTHCHECK --interval=30s --timeout=6s --start-period=25s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=5).status==200 else 1)"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
