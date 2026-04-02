FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV HF_HOME /app/.cache/huggingface

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only torch first to avoid pulling 4GB CUDA packages
RUN pip install --no-cache-dir torch==2.2.0+cpu --index-url https://download.pytorch.org/whl/cpu

# Install remaining python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt --no-deps || pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Try to download the transformer model during build to cache it in the image constraint
# We use a python one-liner to download the model
RUN python -c "from transformers import pipeline; pipeline('token-classification', model='dslim/bert-base-NER')" || echo "Warning: Model download failed during build, it will download at runtime."

# Expose port
EXPOSE 8000

# Command to run the application
# We use a shell-style CMD to allow variable expansion for $PORT
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
