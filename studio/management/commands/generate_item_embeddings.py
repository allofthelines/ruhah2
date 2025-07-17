import base64
import requests
from django.core.management.base import BaseCommand
from studio.models import Item  # Change to your item import path if necessary
from django.conf import settings
from django.core.files.storage import default_storage

DOCSTRING = """
USAGE (interactive mode):

  $ python manage.py generate_item_embeddings

    At the prompt, enter one of:

      [itemid]     - Provide a specific item's itemid (string), e.g. 10920949
                           → Embedding will be generated and overwritten for JUST that item.

      soft-all     - Update all items where embedding is EMPTY (null).
      hard-all     - Overwrite embedding for ALL items, regardless of existing value.

If in doubt, use `soft-all` (update uninitialized only).

Notes:
- Only items with an image file (recommended: PNG) are considered valid.
- If an itemid is used, embedding is ALWAYS re-generated (overwriting any previous embedding).
- If 'hard-all', all embeddings are regenerated regardless of previous value.
- API key must be set at `settings.GOOGLE_API_KEY` and have billing enabled.
"""

class Command(BaseCommand):
    help = "Generate vector embeddings for items using Gemini API. " + DOCSTRING

    def handle(self, *args, **options):
        self.stdout.write(self.help)
        user_input = input(">> Enter itemid, 'soft-all', or 'hard-all': ").strip()

        if user_input.lower() == 'soft-all':
            # Only items with NULL embedding
            qs = Item.objects.filter(embedding__isnull=True)
            mode = 'soft-all'
        elif user_input.lower() == 'hard-all':
            # All items, force overwrite
            qs = Item.objects.all()
            mode = 'hard-all'
        elif user_input:
            # Assume itemid
            mode = 'itemid'
            qs = Item.objects.filter(itemid=user_input)
            if not qs.exists():
                self.stderr.write(self.style.ERROR(
                    f"❌ No Item found with itemid='{user_input}'."
                ))
                return
        else:
            self.stderr.write("❌ No input given. Exiting.")
            return

        self.stdout.write(f"Selected mode: {mode}. {qs.count()} items will be processed.")

        for item in qs:
            # skip if item.embedding exists in soft-all mode (shouldn't happen)
            if mode == 'soft-all' and item.embedding:
                self.stdout.write(self.style.WARNING(f"⚠️  Skipping {item.itemid} (already embedded)"))
                continue
            # skip if item.image is not set
            if not item.image or not item.image.name:
                self.stderr.write(self.style.WARNING(f"⏩ Skipping {item.itemid} (no image)"))
                continue
            try:
                self.process_item(item, force_overwrite=True)
            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    f"❌ Error processing itemid={item.itemid}: {str(e)}"
                ))

        self.stdout.write(self.style.SUCCESS(f"Done."))

    def process_item(self, item, force_overwrite=False):
        """
        Processes one item - generates embedding regardless of previous embedding value
        (force_overwrite==True always for current use cases)
        """
        with default_storage.open(item.image.name, 'rb') as image_file:
            image_data = image_file.read()
        mimetype = "image/png"  # image files are always png per requirements

        description = self.generate_image_description(image_data, mimetype)
        if not description:
            raise Exception("Failed to get a description from Gemini API.")

        vector = self.text_to_vector(description)
        if not isinstance(vector, list) or not vector:
            raise Exception("Failed to obtain a valid vector from Google Multimodal.")

        item.embedding = vector  # Direct assignment of list!
        item.save(update_fields=['embedding'])
        self.stdout.write(self.style.SUCCESS(
            f"✅ {item.itemid or item.id}: embedding updated."
        ))

    def generate_image_description(self, image_data, mimetype):
        api_key = settings.GOOGLE_API_KEY
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key={api_key}"
        prompt = (
            "Describe this fashion item in extreme detail including: "
            "1. Primary colors and color patterns "
            "2. Material types and textures "
            "3. Style characteristics "
            "4. Unique design elements "
            "5. Potential use cases and occasions"
        )
        base64_image = base64.b64encode(image_data).decode('utf-8')
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mimetype,
                            "data": base64_image
                        }
                    }
                ]
            }]
        }
        r = requests.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
        try:
            return data['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            raise Exception(f"Malformed or missing description from Gemini: {data}") from e

    def text_to_vector(self, text):
        api_key = settings.GOOGLE_API_KEY
        url = f"https://multimodal.googleapis.com/v1beta/models/multimodal-embedding-001:embedContent?key={api_key}"
        payload = {"text": text}
        r = requests.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
        try:
            vector_data = data['embedding']['values']
            return vector_data  # <--- JUST RETURN THE LIST
        except Exception as e:
            raise Exception(f"Malformed or missing embedding from Google: {data}") from e