FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install flask requests

# Copy source code
COPY src/ ./src/

# Expose port
EXPOSE 9000

# Run the application
CMD ["python", "src/shadow_twin_engine.py"]
