FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python scripts/generate_proto.py

RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 50051

CMD ["python", "manage.py", "serve"]
