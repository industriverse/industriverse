FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install System Dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install PyTorch (CUDA 12.1)
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Install SCF Dependencies
# (We can mount requirements.txt or copy it)
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt || echo "No requirements.txt found, skipping."

# Set Workspace
WORKDIR /workspace

# Copy Codebase (In production, we might mount this or git clone)
COPY . /workspace

# Entrypoint
COPY docker/runpod/startup.sh /workspace/startup.sh
RUN chmod +x /workspace/startup.sh

ENTRYPOINT ["/workspace/startup.sh"]
