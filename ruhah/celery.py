# ruhah/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ruhah.settings')

app = Celery('ruhah')

app.config_from_object('django.conf:settings', namespace='CELERY')
print("Autodiscovering tasks...")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
print("Autodiscovered tasks!")
