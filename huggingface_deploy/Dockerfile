FROM python:3.11-slim

# Install Z3 Solver and system dependencies
RUN apt-get update && apt-get install -y \
    z3 \
    libz3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Configure Hugging Face security user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"
ENV PYTHONPATH="/app"

# Copy and install dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy DIOTEC 360 IA unified codebase
COPY --chown=user . .

# Expose port 7860 (Hugging Face requirement)
EXPOSE 7860

# Start the Sovereign Judge API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
