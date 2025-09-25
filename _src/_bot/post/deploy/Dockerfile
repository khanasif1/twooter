# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        requests>=2.31.0 \
        beautifulsoup4>=4.12.0 \
        lxml>=4.9.0 \
        html5lib>=1.1 \
        openai>=1.0.0 \
        azure-identity>=1.15.0

# Copy application code
COPY . .

# Create non-root user and set permissions
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app && \
    mkdir -p /app/data && \
    chown appuser:appuser /app/data

# Switch to non-root user
USER appuser

# Default command - runs your workflow
CMD ["python", "post_orchestrator.py", "--run-workflow"]