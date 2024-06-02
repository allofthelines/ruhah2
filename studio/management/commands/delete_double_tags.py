from django.core.management.base import BaseCommand
from studio.models import Item  # Import the Item model

class Command(BaseCommand):
    help = 'Remove duplicate tags from Item instances'

    def handle(self, *args, **kwargs):
        items = Item.objects.all()

        for item in items:
            if item.tags:
                # Split the tags into individual words
                tags = item.tags.split()
                # Remove duplicates by converting the list to a set and then back to a list
                unique_tags = list(set(tags))
                # Join the unique tags back into a single string
                cleaned_tags = ' '.join(unique_tags)
                # Update the item tags if they have changed
                if item.tags != cleaned_tags:
                    item.tags = cleaned_tags
                    item.save()
                    self.stdout.write(self.style.SUCCESS(f'Updated item {item.itemid} tags to: {cleaned_tags}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Item {item.itemid} tags are already unique'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Item {item.itemid} has no tags to update'))
