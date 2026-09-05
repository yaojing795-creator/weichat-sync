FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
COPY . .
EXPOSE 8765
ENV PORT=8765
ENV DB_PATH=/app/data/weichat_sync.db
RUN mkdir -p /app/data
CMD ["gunicorn", "backend.gunicorn_app:application", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8765"]
