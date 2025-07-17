import os
import csv
import ast  # For safe parsing of string lists
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from django.conf import settings
from chatai.models import Product
from chatai.brand_mappings import BRAND_MAPPINGS

class Command(BaseCommand):
    help = "Load products from CSVs in warehouse-csv/ into Product model."

    def handle(self, *args, **options):
        csv_dir = os.path.join(settings.BASE_DIR, 'warehouse-csv')
        if not os.path.exists(csv_dir):
            self.stderr.write("❌ warehouse-csv/ not found.")
            return

        for filename in os.listdir(csv_dir):
            if not filename.endswith('.csv'):
                continue
            brand = filename.split('.')[0]  # e.g., 'zara'
            if brand not in BRAND_MAPPINGS:
                self.stdout.write(f"⚠️ Skipping {filename} (no mapping).")
                continue

            mapping = BRAND_MAPPINGS[brand]
            filepath = os.path.join(csv_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data = {'product_brand': brand}  # Set brand dynamically
                    for csv_col, model_field in mapping.items():
                        value = row.get(csv_col)
                        if value:
                            if model_field == 'product_images':
                                try:
                                    data[model_field] = ast.literal_eval(value)  # Parse string to list of dicts
                                except Exception as e:
                                    self.stdout.write(f"⚠️ Skipping row due to invalid images: {e}")
                                    continue
                            elif model_field == 'product_price':
                                try:
                                    cleaned = value.replace('₹ ', '').replace(',', '')
                                    data[model_field] = Decimal(cleaned)
                                except InvalidOperation:
                                    self.stdout.write(f"⚠️ Skipping row due to invalid price: {value}")
                                    continue
                            else:
                                data[model_field] = value

                    if not data.get('product_link'):  # Skip if no link (required for dupe check)
                        self.stdout.write("⚠️ Skipping row (no link)")
                        continue

                    # Duplicate check: same brand AND link
                    if Product.objects.filter(product_brand=brand, product_link=data['product_link']).exists():
                        self.stdout.write(f"⚠️ Skipping duplicate: {data.get('product_name')} (brand: {brand}, link: {data['product_link']})")
                        continue

                    # Set product_main_image: For now, just pick the first image's URL if available.
                    # FUTURE: Replace this with AI logic to analyze images (e.g., download each URL, use an AI model like Google Vision or custom ML to detect if it shows a single product vs. multiple/full-body.
                    # Example criteria: If category is 'top', prefer zoomed-in images showing only the shirt (e.g., score based on object detection: single item, no full body/jeans).
                    # Could use libraries like OpenCV or APIs to evaluate and select the best URL.
                    product_images = data.get('product_images', [])
                    if product_images and isinstance(product_images, list) and len(product_images) > 0 and 'url' in product_images[0]:
                        data['product_main_image'] = product_images[0]['url']

                    if data:
                        Product.objects.create(**data)
                        self.stdout.write(f"✅ Added {data.get('product_name')} (brand: {brand})")

        self.stdout.write("Done. Total products in DB: " + str(Product.objects.count()))  # Debug: print total after load