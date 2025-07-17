import base64
import os
from django.core.management.base import BaseCommand
from studio.models import Item  # Update import as needed
from django.conf import settings
from django.core.files.storage import default_storage
from PIL import Image
import io

# Import Vertex AI stuff:
from google.oauth2 import service_account
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel

DOCSTRING = """
USAGE (interactive mode):

  $ python manage.py generate_item_embeddings

    At the prompt, enter one of:

      [itemid]     - Provide a specific item's itemid (string), e.g., 10920949
                           → Embedding will be generated and overwritten for JUST that item.

      soft-all     - Update all items where embedding is EMPTY (null).
      hard-all     - Overwrite embedding for ALL items, regardless of existing value.

If in doubt, use `soft-all` (update uninitialized only).

Notes:
- Only items with an image file (recommended: PNG) are considered valid.
- If an itemid is used, embedding is ALWAYS re-generated (overwriting any previous embedding).
- If 'hard-all', all embeddings are regenerated regardless of previous value.
- GOOGLE_VERTEX_SERVICE_ACCOUNT_FILE env variable must be set to JSON service account.
- Project and location are hard-coded below.
- Images are automatically resized to 250x250 px (aspect ratio preserved).
"""

def smart_resize(image_data, max_px=250):
    """Resize the image to fit inside a max_px x max_px box, preserving aspect."""
    with Image.open(io.BytesIO(image_data)) as img:
        img = img.convert("RGB")
        img.thumbnail((max_px, max_px))  # preserves aspect
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf.read()

# === VERTEX AI SETUP (do only once per Python process) ===
SERVICE_ACCOUNT_FILE_PATH = os.environ.get("GOOGLE_VERTEX_SERVICE_ACCOUNT_FILE")
if not SERVICE_ACCOUNT_FILE_PATH or not os.path.exists(SERVICE_ACCOUNT_FILE_PATH):
    raise RuntimeError(
        "GOOGLE_VERTEX_SERVICE_ACCOUNT_FILE env var not set "
        "or does not point to a valid file. Cannot authenticate with Vertex AI!"
    )

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE_PATH,
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

aiplatform.init(
    credentials=creds,
    project="gen-lang-client-0869247041",  # <--- YOUR PROJECT ID
    location="us-central1"
)

# Preload model for efficiency
embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")

class Command(BaseCommand):
    help = "Generate vector embeddings for items using Vertex AI. " + DOCSTRING

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
                self.stderr.write(self.style.ERROR(
                    f"❌ No Item found with itemid='{user_input}'."
                ))
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
        mimetype = "image/png"

        # --- Smart resize ---
        image_data = smart_resize(image_data, 250)

        # Get a description (you can choose another method here if using images)
        description = self.generate_image_description(image_data, mimetype)
        if not description:
            raise Exception("Failed to get a description from Gemini vision/model.")

        # Get the text embedding from Vertex
        vector = self.text_to_vector(description)
        if not isinstance(vector, list) or not vector:
            raise Exception("Failed to obtain embedding from Vertex AI.")

        item.embedding = vector
        item.save(update_fields=['embedding'])
        self.stdout.write(self.style.SUCCESS(
            f"✅ {item.itemid or item.id}: embedding updated."
        ))

    def generate_image_description(self, image_data, mimetype):
        """
        This function uses the Gemini API to describe an image in text (calls REST API directly).
        Switch to Vertex SDK for image description if/when available via Python SDK.
        """
        from google.generativeai import configure, GenerativeModel

        # This step uses your Vertex Gemini model (not the legacy API_KEY method)
        configure(
            credentials=creds,
            project="gen-lang-client-0869247041"
        )
        model = GenerativeModel('gemini-1.5-flash')
        # Gemini expects the image byte data directly
        try:
            response = model.generate_content([
                "Describe this fashion item in extreme detail including: "
                "1. Primary colors and color patterns "
                "2. Material types and textures "
                "3. Style characteristics "
                "4. Unique design elements "
                "5. Potential use cases and occasions",
                image_data
            ])
            return response.text
        except Exception as e:
            raise Exception(f"Error in Gemini generate_content: {e}")

    def text_to_vector(self, text):
        """
        Use Vertex's text embedding model to convert description to vector.
        """
        try:
            embeddings = embedding_model.get_embeddings([text])
            # Returns a list [Embedding], each Embedding has attribute 'values'
            return embeddings[0].values
        except Exception as e:
            raise Exception(f"Error getting embedding from Vertex textembedding-gecko: {e}")