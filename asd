cd src
gunicorn -k uvicorn.workers.UvicornWorker TWC.wsgi:application --bind 0.0.0.0:8000