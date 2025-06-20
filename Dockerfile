# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy only the necessary files
COPY requirements.txt .
COPY bot.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"]