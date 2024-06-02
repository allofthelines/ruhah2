from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import models

class Command(BaseCommand):
    help = 'List all models with their fields and field types'

    def handle(self, *args, **kwargs):
        all_models = apps.get_models()
        for model in all_models:
            self.stdout.write(f"Model: {model.__name__}")
            for field in model._meta.get_fields():
                field_type = type(field).__name__
                if isinstance(field, models.ForeignKey):
                    field_type += f" to {field.related_model.__name__}"
                self.stdout.write(f"  - {field.name}: {field_type}")
            self.stdout.write("")  # Add a blank line for readability
