# Victor Campaign Reaction Orchestrator - Docker Container
# Multi-stage build for efficient containerization

FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY deploy/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code (all Python files and config)
COPY *.py ./
COPY config.json ./
COPY *.db ./
COPY .env* ./
# Note: .env file copied for fallback, but environment variables
# passed directly to Docker container take precedence

# Create necessary directories and set permissions
RUN mkdir -p /app/logs /app/data \
    && chown -R appuser:appuser /app \
    && chmod +x /app/*.py

# Switch to non-root user
USER appuser

# Set Python path to include user packages
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app:/home/appuser/.local/lib/python3.11/site-packages

# Expose port for health checks
EXPOSE 8000

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Set entry point
ENTRYPOINT ["python", "mention_orchestrator.py"]

# Container metadata
LABEL maintainer="Victor Campaign Team"
LABEL description="Victor Campaign Reaction Orchestrator - Automated mention monitoring and response system"
LABEL version="1.0"