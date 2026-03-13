# Dockerfile for Aethel API - Railway Deployment
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy ALL requirements first
COPY requirements.txt ./requirements-core.txt
COPY api/requirements.txt ./requirements-api.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements-core.txt
RUN pip install --no-cache-dir -r requirements-api.txt

# Copy entire application
COPY . .

# Create vault directory
RUN mkdir -p .aethel_vault/bundles .aethel_vault/certificates

# Expose port (Railway will override with $PORT)
EXPOSE 8000

# Use Python script that reads PORT correctly
CMD ["python", "api/run.py"]
