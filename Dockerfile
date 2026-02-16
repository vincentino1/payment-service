# Private Nexus Docker registry 
ARG DOCKER_PRIVATE_REPO=3-98-125-121.sslip.io/myapp-docker-group

#========================
# Stage 1: Builder
#=========================
FROM ${DOCKER_PRIVATE_REPO}/python:3.11-slim AS builder

# Prevent bytecode & enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /install

# System deps needed for psycopg / builds
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependency file first (cache optimization)
COPY requirements.txt .

# Install dependencies into a temp location
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt


# Stage 2: Runtime
# =========================
FROM ${DOCKER_PRIVATE_REPO}/python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5002

WORKDIR /app

# Runtime system deps only
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini .

# Create non-root user
RUN addgroup --system app && adduser --system --group app
RUN chown -R app:app /app
USER app

EXPOSE 5002

# ---------- Healthcheck ----------
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5002/health || exit 1

# Start the service
CMD ["python", "-m", "src.server"]
