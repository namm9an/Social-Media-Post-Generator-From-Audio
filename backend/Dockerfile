# Backend Dockerfile for AI Social Media Post Generator
# Multi-stage build for production optimization

# Stage 1: Build stage with development dependencies
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ffmpeg \
    libsndfile1 \
    libsox-fmt-all \
    sox \
    git \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/opt/venv/bin:$PATH" \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    WHISPER_MODEL=base \
    MAX_WORKERS=4 \
    UPLOAD_FOLDER=/app/uploads/audio \
    DATA_FOLDER=/app/uploads/data \
    CORS_ORIGINS=*

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    libsox-fmt-all \
    sox \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /bin/bash appuser

# Create application directory and set ownership
WORKDIR /app
RUN mkdir -p /app/uploads/audio /app/uploads/data /app/models /app/logs && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . .

# Create .env file with defaults
RUN echo "WHISPER_MODEL=base\nMAX_WORKERS=4\nUPLOAD_FOLDER=/app/uploads/audio\nDATA_FOLDER=/app/uploads/data\nCORS_ORIGINS=*" > .env

# Switch to non-root user
USER appuser

# Download Whisper model at build time to cache it
RUN python -c "import whisper; whisper.load_model('base')" || echo "Whisper model will be downloaded at runtime"

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Expose port
EXPOSE 5000

# Create startup script for better process management
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Ensure directories exist\n\
mkdir -p /app/uploads/audio /app/uploads/data /app/models /app/logs\n\
\n\
# Start the Flask application\n\
exec python app.py' > /app/start.sh && chmod +x /app/start.sh

# Use startup script as entrypoint
CMD ["/app/start.sh"]
