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
                    data = {}
                    for csv_col, model_field in mapping.items():
                        value = row.get(csv_col)
                        if value:
                            if model_field == 'product_images':
                                try:
                                    data[model_field] = ast.literal_eval(value)  # Parse string to list of dicts
                                except:
                                    continue  # Skip invalid
                            elif model_field == 'product_price':
                                try:
                                    cleaned = value.replace('₹ ', '').replace(',', '')
                                    data[model_field] = Decimal(cleaned)
                                except InvalidOperation:
                                    continue
                            else:
                                data[model_field] = value
                    if data:
                        Product.objects.create(**data)
                        self.stdout.write(f"✅ Added {data.get('product_name')}")

        self.stdout.write("Done.")