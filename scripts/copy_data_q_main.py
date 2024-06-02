import os
import django
from django.apps import apps
from django.db import connections, transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()

def copy_data(from_db, to_db):
    for model in apps.get_models():
        from_queryset = model.objects.using(from_db).all()
        with transaction.atomic(using=to_db):
            model.objects.using(to_db).bulk_create(from_queryset)

if __name__ == "__main__":
    copy_data('q', 'default')
