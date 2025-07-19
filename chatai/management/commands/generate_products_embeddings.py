import os
import io
import requests  # For downloading image from URL
from django.core.management.base import BaseCommand
from chatai.models import Product  # Use Product instead of Item
import google.generativeai as genai
from PIL import Image

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

  $ python manage.py generate_products_embeddings

    At the prompt, enter one of:
      [product ID] - Provide a specific product's ID (integer), e.g., 5
      soft-all     - Update all products where embedding is EMPTY (null).
      hard-all     - Overwrite embedding for ALL products, regardless of existing value.
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
    help = "Generate vector embeddings for products using Google Generative AI. " + DOCSTRING

    def handle(self, *args, **options):
        self.stdout.write(self.help)

        while True:  # Loop until valid input
            user_input = input(">> Enter product ID (integer), 'soft-all', or 'hard-all': ").strip()

            if user_input.lower() == 'soft-all':
                qs = Product.objects.filter(product_embedding__isnull=True)
                mode = 'soft-all'
                break
            elif user_input.lower() == 'hard-all':
                qs = Product.objects.all()
                mode = 'hard-all'
                break
            elif user_input:
                mode = 'product_id'
                try:
                    product_id = int(user_input)  # Expect integer ID
                    qs = Product.objects.filter(id=product_id)
                    if not qs.exists():
                        self.stderr.write(
                            self.style.ERROR(f"Hey, this product ID ({product_id}) does not exist, try again."))
                        continue  # Re-prompt
                    break
                except ValueError:
                    self.stderr.write(self.style.ERROR(
                        "Invalid input. Please enter a valid integer product ID, 'soft-all', or 'hard-all'."))
                    continue  # Re-prompt
            else:
                self.stderr.write("❌ No input given. Exiting.")
                return

        self.stdout.write(f"Selected mode: {mode}. {qs.count()} products will be processed.")

        for product in qs:
            if mode == 'soft-all' and product.product_embedding:
                self.stdout.write(self.style.WARNING(f"⚠️  Skipping {product.id} (already embedded)"))
                continue
            try:
                self.process_product(product, mode)
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"❌ Error processing product ID={product.id}: {str(e)}"))
        self.stdout.write(self.style.SUCCESS("Done."))

    def process_product(self, product, mode):
        # Check for product_images (list) and ensure at least 1 image
        if not product.product_images or not isinstance(product.product_images, list) or len(product.product_images) < 1:
            self.stdout.write(self.style.WARNING(f"⏩ Skipping {product.id} (no images in product_images)"))
            return

        # Search for an S3 image URL containing 'amazonaws' (prioritize second if available, else first matching)
        selected_image_url = None
        image_note = None

        # First, try to find in preferred order: second image if it has 'amazonaws', then scan others
        if len(product.product_images) >= 2:
            second_image = product.product_images[1]
            if isinstance(second_image, dict) and len(second_image) == 1:
                url = next(iter(second_image))  # Get the key (which is the URL)
                if url.startswith('http') and 'amazonaws' in url:
                    selected_image_url = url
                    image_note = "second (S3)"

        # If not found, scan all images for the first one with 'amazonaws'
        if selected_image_url is None:
            for idx, image_entry in enumerate(product.product_images):
                if isinstance(image_entry, dict) and len(image_entry) == 1:
                    url = next(iter(image_entry))  # Get the key (which is the URL)
                    if url.startswith('http') and 'amazonaws' in url:
                        selected_image_url = url
                        image_note = f"index {idx} (S3)"
                        break  # Use the first matching S3 URL

        # If no S3 URL found (no 'amazonaws' in any key), skip regardless of mode
        if selected_image_url is None:
            print(f"DEBUG: No S3 image URL ('amazonaws') found in product_images for ID={product.id}: {product.product_images}")  # For troubleshooting; remove if not needed
            self.stdout.write(self.style.WARNING(f"⏩ Skipping {product.id} (no S3 image URL with 'amazonaws')"))
            return

        # Download image from the selected URL (handles jpg, png, webp, etc.)
        try:
            response = requests.get(selected_image_url, timeout=10)
            response.raise_for_status()  # Raise if download fails (e.g., 404)
            image_bytes = response.content
        except requests.RequestException as e:
            raise Exception(f"Failed to download image from URL: {e}")

        # FUTURE: Instead of downloading from URL each time, migrate to storing images in AWS S3 with a proper ImageField (like in Item model).
        # Download images once to a folder like product-main-images in S3 during loading, and use the S3 path for both website purposes (ruhah display)
        # and embeddings generation. This would be more efficient for caching/reuse and avoid repeated downloads.

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

        product.product_embedding = vector
        product.save(update_fields=["product_embedding"])
        self.stdout.write(self.style.SUCCESS(f"✅ {product.id}: embedding updated (using {image_note} image)."))

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