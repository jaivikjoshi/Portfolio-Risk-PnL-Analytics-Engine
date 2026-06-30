FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md ./
COPY app ./app
COPY alembic ./alembic
COPY scripts ./scripts
COPY data ./data

RUN pip install --no-cache-dir -e ".[postgres]"

EXPOSE 8000

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

