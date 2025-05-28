FROM python:3.11-slim

LABEL maintainer="Industriverse Protocol Layer Team"
LABEL description="Industriverse Protocol Layer - The Maestro of the Industrial Foundry Framework"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PROTOCOL_HOME=/opt/industriverse/protocol
ENV CONFIG_DIR=${PROTOCOL_HOME}/config
ENV LOG_DIR=${PROTOCOL_HOME}/logs
ENV DATA_DIR=${PROTOCOL_HOME}/data

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libssl-dev \
    netcat-openbsd \
    openssl \
    jq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p ${PROTOCOL_HOME} \
    ${CONFIG_DIR} \
    ${LOG_DIR} \
    ${DATA_DIR}

# Set working directory
WORKDIR ${PROTOCOL_HOME}

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy protocol layer code
COPY . ${PROTOCOL_HOME}/

# Make entrypoint script executable
RUN chmod +x ${PROTOCOL_HOME}/entrypoint.sh

# Expose ports
# Main protocol API port
EXPOSE 8080
# Metrics port
EXPOSE 9090
# Admin port
EXPOSE 8081

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]
