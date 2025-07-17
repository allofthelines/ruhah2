import os
import json
from django.core.management.base import BaseCommand
from studio.models import Item
from django.conf import settings
from django.core.files.storage import default_storage
from PIL import Image # Gemini wants a PIL.Image.Image! Not bytes.
import io

from google.oauth2 import service_account
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel

# ----------- SERVICE ACCOUNT HANDLING (WORKS LOCALLY and on HEROKU) -----------
def ensure_gcp_sa_file():
    """
    Ensures a Google service account key file exists on disk,
    regardless of whether JSON is supplied as a config var or as a filename.

    Returns the path to the key file to use, or raises on failure.
    """
    json_from_env = os.environ.get("GOOGLE_VERTEX_SERVICE_ACCOUNT_JSON")
    file_from_env = os.environ.get("GOOGLE_VERTEX_SERVICE_ACCOUNT_FILE")

    # -- Heroku/production-style: JSON is in env, not a file on disk
    if json_from_env:
        sa_path = "/tmp/gcp-sa-key.json"
        with open(sa_path, "w") as f:
            if json_from_env.strip().startswith('{'):
                f.write(json_from_env)
            else:
                # Fix for possible accidentally base64-encoded JSON
                import base64
                try:
                    f.write(base64.b64decode(json_from_env).decode("utf-8"))
                except Exception:
                    raise RuntimeError("Incomplete/bad service account JSON in config var")
        return sa_path

    # -- Local/dev-style: File on disk
    if file_from_env and os.path.exists(file_from_env):
        return file_from_env

    raise RuntimeError(
        "No valid service account found! Set GOOGLE_VERTEX_SERVICE_ACCOUNT_FILE to a key file (locally),\n"
        "or set GOOGLE_VERTEX_SERVICE_ACCOUNT_JSON (on Heroku, containing the _full_ JSON key as a string/config var)"
    )

# Actually get our key file
SERVICE_ACCOUNT_FILE_PATH = ensure_gcp_sa_file()
print("DEBUG: Service account path being used:", SERVICE_ACCOUNT_FILE_PATH)

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE_PATH,
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

aiplatform.init(
    credentials=creds,
    project="gen-lang-client-0869247041",
    location="us-central1"
)
embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")

DOCSTRING = """
USAGE (interactive mode):

  $ python manage.py generate_item_embeddings

    At the prompt, enter one of:
      [itemid]     - Provide a specific item's itemid (string), e.g., 10920949
      soft-all     - Update all items where embedding is EMPTY (null).
      hard-all     - Overwrite embedding for ALL items, regardless of existing value.

If in doubt, use `soft-all` (update uninitialized only).
Notes:
- Only items with an image file (recommended: PNG) are considered valid.
- GOOGLE_VERTEX_SERVICE_ACCOUNT_FILE env variable (or _JSON on Heroku) must be set to JSON service account.
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
        with default_storage.open(item.image.name, 'rb') as image_file:
            image_data = image_file.read()
        mimetype = "image/png"
        image_data = smart_resize(image_data, 250)
        description = self.generate_image_description(image_data, mimetype)
        if not description:
            raise Exception("Failed to get a description from Gemini vision/model.")

        vector = self.text_to_vector(description)
        if not isinstance(vector, list) or not vector:
            raise Exception("Failed to obtain embedding from Vertex AI.")

        item.embedding = vector
        item.save(update_fields=['embedding'])
        self.stdout.write(self.style.SUCCESS(
            f"✅ {item.itemid or item.id}: embedding updated."
        ))

    def generate_image_description(self, image_data, mimetype):
        from google.generativeai import configure, GenerativeModel

        configure(
            credentials=creds
            # project="gen-lang-client-0869247041" to eixa kai to evgala giati error
        )
        model = GenerativeModel('gemini-1.5-flash')
        try:
            img_obj = Image.open(io.BytesIO(image_data))
            response = model.generate_content([
                "Describe this fashion item in extreme detail including: "
                "1. Primary colors and color patterns "
                "2. Material types and textures "
                "3. Style characteristics "
                "4. Unique design elements "
                "5. Potential use cases and occasions",
                img_obj
            ])
            return response.text
        except Exception as e:
            raise Exception(f"Error in Gemini generate_content: {e}")

    def text_to_vector(self, text):
        try:
            embeddings = embedding_model.get_embeddings([text])
            return embeddings[0].values
        except Exception as e:
            raise Exception(f"Error getting embedding from Vertex textembedding-gecko: {e}")