import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from studio.models import Item  # Import the Item model

class Command(BaseCommand):
    help = 'Write images to Item instances from media/items-new folder and move them to media/items folder'

    def handle(self, *args, **kwargs):
        # Define the path to the media/items-new and media/items directories
        media_items_new_path = os.path.join(settings.MEDIA_ROOT, 'items-new')
        media_items_path = os.path.join(settings.MEDIA_ROOT, 'items')

        # Check if the items-new directory exists
        if not os.path.exists(media_items_new_path):
            self.stdout.write(self.style.ERROR(f'The directory {media_items_new_path} does not exist.'))
            return

        # Iterate over the files in the media/items-new directory
        for filename in os.listdir(media_items_new_path):
            if filename.endswith('.png'):
                # Extract the item_id from the filename (assuming the format is <item_id>.png)
                item_id = os.path.splitext(filename)[0]

                try:
                    # Try to get the Item instance by itemid
                    item = Item.objects.get(itemid=item_id)

                    # Check if the image field is set to the default image
                    if item.image.name == 'items/default.jpg':
                        item.image = os.path.join('items', filename)
                        item.save()
                        self.stdout.write(self.style.SUCCESS(f'Successfully updated image for item with id: {item_id}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Item with id {item_id} already has a custom image'))
            

                    # Move the file from items-new to items directory
                    # filename == 123.png
                    src = os.path.join(media_items_new_path, filename)
                    dst = os.path.join(media_items_path, filename)
                    shutil.move(src, dst)
                    self.stdout.write(self.style.SUCCESS(f'Successfully moved image {filename} to {media_items_path}'))
                    
                except Item.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Item with id {item_id} does not exist'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing item with id {item_id}: {e}'))
