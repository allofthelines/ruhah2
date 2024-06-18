"""from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ruhah.settings')

app = Celery('ruhah')

# app.config_from_object(settings, namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')"""

# celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ruhah.settings')

app = Celery('ruhah')

if getattr(settings, 'CELERY_ENABLED', True):
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

    @app.task(bind=True)
    def debug_task(self):
        print(f'Request: {self.request!r}')
else:
    @app.task(bind=True)
    def debug_task(self):
        print('Celery is disabled')

