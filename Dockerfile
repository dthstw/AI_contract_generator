# Use Python 3.10 slim image as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy source code first
COPY src/ ./src/
COPY api.py index.html ./
COPY pyproject.toml requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -e .

# Create contracts directory
RUN mkdir -p contracts

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Default command - run the web server
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"] 