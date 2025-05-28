FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs generative_layer_storage offer_templates

# Set permissions
RUN chmod +x entrypoint.sh

# Expose ports
EXPOSE 8082 8083

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]
