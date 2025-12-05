# Base image with PyTorch and CUDA support
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# Set working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
  git \
  curl \
  unzip \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# We include b2sdk for the fossil shuttle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt b2sdk

# Copy source code
COPY src/ src/
COPY scripts/ scripts/

# Set Python path
ENV PYTHONPATH=/workspace

# Default command (can be overridden)
CMD ["python3", "scripts/train_ebdm_tiny.py"]
