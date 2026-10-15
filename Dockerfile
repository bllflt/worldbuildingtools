# Stage 1: Build dependencies
FROM python:3.14-slim AS builder

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements file first to leverage Docker layer cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir numpy torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install -U sentence-transformers

# Stage 2: Final minimal run-time image
FROM python:3.14-slim AS runner

WORKDIR /app

# Create non-root system user and group for security
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -m -s /sbin/nologin appuser && \
    install -d -o appuser -g appgroup /app/data/images
ENV IMAGE_DIR=/app/data/images


# Install runtime utilities (like curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtualenv from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Pre-download and cache the specific model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copy application source code
COPY --chown=appuser:appgroup src/ ./src/

# Create directory for image storage (as configured in config.py) and change ownership
RUN mkdir -p /app/data/images && chown -R appuser:appgroup /app

# Switch to the non-root user
#USER appuser

# Expose application port
EXPOSE 2000

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Simple healthcheck to verify container health
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:2000/docs || exit 1

# Run the FastAPI application using uvicorn
CMD ["uvicorn", "charservice.main:app", "--host", "0.0.0.0", "--port", "2000"]
