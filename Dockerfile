FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY requirements-minimal.txt .
RUN pip install --no-cache-dir -r requirements-minimal.txt

COPY . .
RUN python scripts/ingest_knowledge_base.py

EXPOSE 8000 8501
CMD ["uvicorn", "safetyreview_ai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
