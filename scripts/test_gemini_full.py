import os
import google.generativeai as genai
from PIL import Image
import io
import requests  # For downloading sample image if needed

# Configure with your API key
API_KEY = os.environ.get("GOOGLE_API_KEY")
API_KEY = "AIzaSyABrLYaoB4yDJdDEKBjwmJ3PYsi17Wkhks"
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set!")
genai.configure(api_key=API_KEY)

# Models to test
DESCRIPTION_MODEL = "models/gemini-1.5-flash"  # For text/image generation
EMBEDDING_MODEL = "models/embedding-001"  # For embeddings

def list_models():
    print("Listing available models...")
    for model in genai.list_models():
        print(f"Model: {model.name}")
        print(f"Supported Methods: {model.supported_generation_methods}")
        print("---")

def test_text_generation():
    print("\nTesting text-only generation...")
    try:
        model = genai.GenerativeModel(DESCRIPTION_MODEL)
        response = model.generate_content("Describe a red t-shirt in detail.")
        print("Response:", response.text)
    except Exception as e:
        print(f"Error: {e}")

def test_multimodal_generation(image_path):
    print("\nTesting image + text (multimodal) generation...")
    try:
        # Load and resize image (like in your script)
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        img = Image.open(io.BytesIO(image_bytes))
        img.thumbnail((250, 250))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        image_data = buf.getvalue()

        model = genai.GenerativeModel(DESCRIPTION_MODEL)
        image_file = {
            'mime_type': 'image/png',
            'data': image_data
        }
        prompt = "Describe this fashion item in extreme detail."
        response = model.generate_content([prompt, image_file])
        print("Response:", response.text)
    except Exception as e:
        print(f"Error: {e}")

def test_embedding():
    print("\nTesting text embedding...")
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content="This is a test sentence about fashion.",
            task_type="retrieval_document"
        )
        vector = result['embedding']
        print("Embedding sample (first 10 values):", vector[:10])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_models()  # Should show models like in your previous test
    test_text_generation()  # Simple text test
    # Replace with your image path (e.g., "~/test_image.png" or a real item image)
    test_multimodal_generation("/Users/aris/Documents/1-RUHAH/1-website/ruhah-heroku/ruhah2/media/items/10920949.png")  # Update this path!
    test_embedding()  # Embedding test