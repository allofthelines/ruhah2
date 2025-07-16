import base64
import requests
from django.core.management.base import BaseCommand
from studio.models import Item
from django.conf import settings
from pgvector.django import Vector
from django.core.files.storage import default_storage

class Command(BaseCommand):
    help = 'Generates vector embeddings for items using Gemini API'
    
    def add_arguments(self, parser):
        parser.add_argument('--overwrite', action='store_true', help='Regenerate embeddings even if they exist')
        parser.add_argument('--limit', type=int, default=0, help='Max number of items to process')
    
    def handle(self, *args, **options):
        items = self.get_items_to_process(options['overwrite'], options['limit'])
        self.stdout.write(f"Processing {len(items)} items...")
        
        for item in items:
            self.process_item(item)
    
    def get_items_to_process(self, overwrite=False, limit=0):
        """Get items without embeddings or all items if overwrite"""
        qs = Item.objects.all()
        
        if not overwrite:
            qs = qs.filter(embedding__isnull=True)
        
        if limit > 0:
            qs = qs[:limit]
            
        return qs
    
    def process_item(self, item):
        """Process an individual item"""
        if not item.image:
            self.stdout.write(f"❌ Skipping item {item.id} - no image")
            return
            
        try:
            # Read image from storage
            with default_storage.open(item.image.name, 'rb') as image_file:
                image_data = image_file.read()
            
            # Generate detailed description
            description = self.generate_image_description(image_data)
            
            # Generate vector from description
            vector = self.text_to_vector(description)
            
            # Save vector to item
            item.embedding = vector
            item.save()
            self.stdout.write(f"✅ Generated vector for item {item.id} - {item.name}")
        except Exception as e:
            self.stderr.write(f"❌ Error processing item {item.id}: {str(e)}")
    
    def generate_image_description(self, image_data):
        """Send image to Gemini API and return detailed description"""
        api_key = settings.GOOGLE_API_KEY
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key={api_key}"
        
        # Encode image as base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": "Describe this fashion item in extreme detail including: "
                             "1. Primary colors and color patterns "
                             "2. Material types and textures "
                             "3. Style characteristics "
                             "4. Unique design elements "
                             "5. Potential use cases and occasions"},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": base64_image
                        }
                    }
                ]
            }]
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    
    def text_to_vector(self, text):
        """Convert text to vector using Google Multimodal API"""
        api_key = settings.GOOGLE_API_KEY
        url = f"https://multimodal.googleapis.com/v1beta/models/multimodal-embedding-001:embedContent?key={api_key}"
        
        payload = {
            "model": "multimodal-embedding-001",
            "text": text
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        vector_data = response.json()['embedding']['values']
        return Vector(vector_data)