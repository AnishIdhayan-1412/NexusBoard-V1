# ============================================================
# NexusBoard Dockerfile - Production-ready multi-stage build
# ============================================================

# Stage 1: Build dependencies
FROM python:3.12-slim as builder

WORKDIR /app

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production image
FROM python:3.12-slim

# Security: run as non-root user
RUN addgroup --system nexus && adduser --system --group nexus

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /home/nexus/.local

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p logs media staticfiles \
    && chown -R nexus:nexus /app

# Switch to non-root user
USER nexus

# Add local bin to PATH
ENV PATH=/home/nexus/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=nexusboard.settings

# Collect static files at build time
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Healthcheck for Docker / Railway / Render
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1

# Start Gunicorn (production WSGI server)
CMD ["gunicorn", "nexusboard.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--threads", "2", \
     "--worker-class", "gthread", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]
