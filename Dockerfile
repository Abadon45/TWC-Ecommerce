FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=TWC.settings.production

WORKDIR /app

# psycopg2 may need the PostgreSQL client headers when dependencies are built.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY src/requirements.txt /app/src/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/src/requirements.txt

COPY src /app/src

WORKDIR /app/src
RUN mkdir -p /app/src/TWC/logs
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "TWC.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
