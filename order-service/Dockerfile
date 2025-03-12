FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY main.py .

RUN pip install uv && \
    uv venv && \
    . .venv/bin/activate && \
    uv pip install --no-cache-dir -r requirements.txt

EXPOSE 8003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
