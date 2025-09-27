# Multi-stage build for the trending engagement bot
FROM python:3.12-slim as builder

# Set build arguments for flexibility
ARG DEBIAN_FRONTEND=noninteractive

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.12-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH=/root/.local/bin:$PATH

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app directory and user
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application files
COPY *.py ./
COPY config.json ./
COPY .env ./

# Create directory for database and logs
RUN mkdir -p /app/data /app/logs

# Set proper permissions
RUN chmod +x *.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Expose port for health checks (optional)
EXPOSE 8000

# Default command - runs the trending orchestrator
CMD ["python", "trending_orchestrator.py"]

# Alternative commands for debugging:
# CMD ["python", "-c", "import sys; print(f'Python {sys.version}'); from trending_orchestrator import *; print('All modules imported successfully')"]
# CMD ["bash"]