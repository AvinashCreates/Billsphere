FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

RUN useradd --create-home --shell /bin/bash celeryuser \
    && chown -R celeryuser:celeryuser /app

USER celeryuser