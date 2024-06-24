import os
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.conf import settings
from studio.models import Item  # Import the Item model
from django.core.files.base import ContentFile


class Command(BaseCommand):
    help = 'Write images to Item instances from media/items-temp folder and move them to media/items folder'

    def handle(self, *args, **kwargs):
        # Define the path to the media/items-new and media/items directories
        media_items_new_path = 'items-temp/'
        media_items_path = 'items/'

        # Check if the items-temp directory exists
        if not default_storage.exists(media_items_new_path):
            self.stdout.write(self.style.ERROR(f'The directory {media_items_new_path} does not exist.'))
            return

        # List files in the items-temp directory
        files = default_storage.listdir(media_items_new_path)[1]

        # Iterate over the files in the media/items-temp directory
        for filename in files:
            if filename.endswith('.png'):
                # Extract the item_id from the filename (assuming the format is <item_id>.png)
                item_id = os.path.splitext(filename)[0]

                try:
                    # Try to get the Item instance by itemid
                    item = Item.objects.get(itemid=item_id)

                    # Check if the image field is set to the default image
                    if item.image.name == 'items/default.jpg':
                        # Read the file from the storage
                        file_path = os.path.join(media_items_new_path, filename)
                        file_content = default_storage.open(file_path).read()
                        item.image.save(os.path.join(media_items_path, filename), ContentFile(file_content), save=False)
                        item.save()
                        self.stdout.write(self.style.SUCCESS(f'Successfully updated image for item with id: {item_id}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Item with id {item_id} already has a custom image'))

                    # Move the file from items-temp to items directory
                    src = os.path.join(media_items_new_path, filename)
                    dst = os.path.join(media_items_path, filename)
                    file_content = default_storage.open(src).read()
                    default_storage.save(dst, ContentFile(file_content))
                    default_storage.delete(src)
                    self.stdout.write(self.style.SUCCESS(f'Successfully moved image {filename} to {media_items_path}'))

                except Item.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Item with id {item_id} does not exist'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing item with id {item_id}: {e}'))
