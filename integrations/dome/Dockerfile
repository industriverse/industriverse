FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire Dome source code
COPY src/ ./src/
COPY *.py ./

# Expose port
EXPOSE 8080

# Run the actual Dome platform
CMD ["python", "dome_main_server.py"]
