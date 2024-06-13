# to evala gia na katharizei to useritemcarts kathe 6 wres
# den doulevei idk giati

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ruhah.settings')

app = Celery('ruhah')

app.config_from_object('django.conf:settings', namespace='CELERY')
print("Autodiscovering tasks from: ", settings.INSTALLED_APPS)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
print("Autodiscovered tasks!")

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    print("Setting up periodic tasks...")
    from accounts.tasks import test_task, clear_user_item_cart
    sender.register_task(test_task)
    sender.register_task(clear_user_item_cart)
    print(f"Registered task: {test_task.name}")
    print(f"Registered task: {clear_user_item_cart.name}")

@app.on_after_finalize.connect
def setup_periodic_tasks_finalize(sender, **kwargs):
    print("Finalizing periodic tasks setup...")
    from accounts.tasks import test_task, clear_user_item_cart
    sender.register_task(test_task)
    sender.register_task(clear_user_item_cart)
    print(f"Manually registered task: {test_task.name}")
    print(f"Manually registered task: {clear_user_item_cart.name}")
