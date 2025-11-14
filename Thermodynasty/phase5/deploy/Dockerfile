# Multi-stage Dockerfile for Industriverse EIL Platform
# Optimized for production deployment

# ============================================================================
# Stage 1: Base Image with System Dependencies
# ============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1000 eil && \
    mkdir -p /app && \
    chown -R eil:eil /app

WORKDIR /app

# ============================================================================
# Stage 2: Dependencies
# ============================================================================
FROM base as dependencies

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ============================================================================
# Stage 3: Application
# ============================================================================
FROM dependencies as application

# Copy application code
COPY --chown=eil:eil . /app/

# Copy phase5 modules
COPY --chown=eil:eil phase5/ /app/phase5/

# Copy Thermodynasty dependencies (existing phase0-4)
COPY --chown=eil:eil ../phase0/ /app/phase0/
COPY --chown=eil:eil ../phase1/ /app/phase1/
COPY --chown=eil:eil ../phase2/ /app/phase2/
COPY --chown=eil:eil ../phase3/ /app/phase3/
COPY --chown=eil:eil ../phase4/ /app/phase4/

# Create necessary directories
RUN mkdir -p /app/data/energy_maps \
             /app/checkpoints \
             /app/logs \
             /app/.cache && \
    chown -R eil:eil /app

# Switch to app user
USER eil

# Expose ports
EXPOSE 8000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# Default command
CMD ["uvicorn", "phase5.api.eil_gateway:app", "--host", "0.0.0.0", "--port", "8000"]

# ============================================================================
# Stage 4: Development (with additional tools)
# ============================================================================
FROM application as development

USER root

# Install development tools
RUN pip install \
    ipdb \
    pytest-watch \
    black \
    flake8 \
    mypy

USER eil

# Override CMD for development
CMD ["uvicorn", "phase5.api.eil_gateway:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================================================
# Stage 5: Production (minimal, optimized)
# ============================================================================
FROM python:3.11-slim as production

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1000 eil && \
    mkdir -p /app && \
    chown -R eil:eil /app

WORKDIR /app

# Copy only necessary files from application stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=application --chown=eil:eil /app /app

# Switch to app user
USER eil

# Expose ports
EXPOSE 8000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# Production command with Gunicorn
CMD ["gunicorn", "phase5.api.eil_gateway:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
