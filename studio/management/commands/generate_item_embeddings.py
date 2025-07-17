import os
import io
from django.core.management.base import BaseCommand
from studio.models import Item
from django.core.files.storage import default_storage
from PIL import Image
import google.generativeai as genai

# Configure the SDK with your API key (from env var)
API_KEY = os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY environment variable is not set!")
genai.configure(api_key=API_KEY)

# Models from your successful test
DESCRIPTION_MODEL = "gemini-1.5-flash"  # For text/image generation (multimodal)
EMBEDDING_MODEL = "models/embedding-001"  # For text embeddings

DOCSTRING = """
USAGE (interactive mode):

  $ python manage.py generate_item_embeddings

    At the prompt, enter one of:
      [itemid]     - Provide a specific item's itemid (string), e.g., 10920949
      soft-all     - Update all items where embedding is EMPTY (null).
      hard-all     - Overwrite embedding for ALL items, regardless of existing value.
"""

def smart_resize(image_data, max_px=250):
    with Image.open(io.BytesIO(image_data)) as img:
        img = img.convert("RGB")
        img.thumbnail((max_px, max_px))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf.read()

class Command(BaseCommand):
    help = "Generate vector embeddings for items using Google Generative AI. " + DOCSTRING

    def handle(self, *args, **options):
        self.stdout.write(self.help)
        user_input = input(">> Enter itemid, 'soft-all', or 'hard-all': ").strip()
        if user_input.lower() == 'soft-all':
            qs = Item.objects.filter(embedding__isnull=True)
            mode = 'soft-all'
        elif user_input.lower() == 'hard-all':
            qs = Item.objects.all()
            mode = 'hard-all'
        elif user_input:
            mode = 'itemid'
            qs = Item.objects.filter(itemid=user_input)
            if not qs.exists():
                self.stderr.write(self.style.ERROR(f"❌ No Item found with itemid='{user_input}'."))
                return
        else:
            self.stderr.write("❌ No input given. Exiting.")
            return

        self.stdout.write(f"Selected mode: {mode}. {qs.count()} items will be processed.")

        for item in qs:
            if mode == 'soft-all' and item.embedding:
                self.stdout.write(self.style.WARNING(f"⚠️  Skipping {item.itemid} (already embedded)"))
                continue
            if not item.image or not item.image.name:
                self.stdout.write(self.style.WARNING(f"⏩ Skipping {item.itemid} (no image)"))
                continue
            try:
                self.process_item(item)
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"❌ Error processing itemid={item.itemid}: {str(e)}"))
        self.stdout.write(self.style.SUCCESS("Done."))

    def process_item(self, item):
        with default_storage.open(item.image.name, "rb") as f:
            image_bytes = f.read()
        image_data = smart_resize(image_bytes, 250)
        prompt = (
            "Describe this fashion item in extreme detail including: "
            "1. Primary colors and color patterns "
            "2. Material types and textures "
            "3. Style characteristics "
            "4. Unique design elements "
            "5. Potential use cases and occasions"
        )
        description = self.generate_image_description(image_data, prompt)
        if not description:
            raise Exception("Failed to get a description from Gemini model.")

        print("DEBUG: Generated description:", description)  # For troubleshooting

        vector = self.text_to_vector(description)
        if not isinstance(vector, list) or not vector:
            raise Exception("Failed to obtain embedding from Google Generative AI.")

        item.embedding = vector
        item.save(update_fields=["embedding"])
        self.stdout.write(self.style.SUCCESS(f"✅ {item.itemid or item.id}: embedding updated."))

    def generate_image_description(self, image_data, prompt):
        try:
            model = genai.GenerativeModel(DESCRIPTION_MODEL)
            # Prepare image as a dict for the SDK
            image_file = {
                'mime_type': 'image/png',
                'data': image_data
            }
            response = model.generate_content([prompt, image_file])
            print("DEBUG: Raw response from Gemini:", response)  # For troubleshooting
            return response.text
        except Exception as e:
            raise Exception(f"Error in Gemini generate_content: {e}")

    def text_to_vector(self, text):
        try:
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_document"  # Good for your use case; can change to "semantic_similarity" if needed
            )
            vector = result['embedding']
            print("DEBUG: Generated embedding vector sample:", vector[:10])  # For troubleshooting
            return vector
        except Exception as e:
            raise Exception(f"Error getting embedding: {e}")