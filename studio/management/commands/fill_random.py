import os
import sys
import django
import random
from django.core.management.base import BaseCommand
from studio.models import Item  # Import the Item model

# Add the project directory to the Python path
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_path)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ruhah.settings')
django.setup()

class Command(BaseCommand):
    help = 'Set random choices for fields with choices in Item model if they are not set to a valid choice'

    def handle(self, *args, **kwargs):
        items = Item.objects.all()

        for item in items:
            updated = False
            for field in item._meta.fields:
                if field.choices:
                    current_value = getattr(item, field.name)
                    valid_choices = [choice[0] for choice in field.choices]
                    if current_value not in valid_choices:
                        new_value = random.choice(valid_choices)
                        setattr(item, field.name, new_value)
                        updated = True
                        self.stdout.write(self.style.SUCCESS(
                            f'Set field {field.name} for item {item.itemid} to random choice {new_value}'
                        ))

            if updated:
                item.save()
                self.stdout.write(self.style.SUCCESS(f'Updated item {item.itemid} with random choices.'))

        self.stdout.write(self.style.SUCCESS('Finished updating items with random choices.'))

