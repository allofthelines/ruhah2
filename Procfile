release: python manage.py migrate --noinput
web: gunicorn ruhah.wsgi

worker: celery -A ruhah worker --loglevel=info
beat: celery -A ruhah beat --loglevel=info
