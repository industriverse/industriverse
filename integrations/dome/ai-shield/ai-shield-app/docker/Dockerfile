FROM python:3.11-slim

WORKDIR /app

RUN pip install fastapi uvicorn httpx

COPY src/ .

EXPOSE 8080

CMD ["python", "main.py"]
