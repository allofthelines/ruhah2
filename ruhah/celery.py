# ruhah/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from accounts.tasks import test_task, clear_user_item_cart

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ruhah.settings')

app = Celery('ruhah')

app.config_from_object('django.conf:settings', namespace='CELERY')
print("Autodiscovering tasks from: ", settings.INSTALLED_APPS)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
print("Autodiscovered tasks!")

app.tasks.register(test_task)
app.tasks.register(clear_user_item_cart)
