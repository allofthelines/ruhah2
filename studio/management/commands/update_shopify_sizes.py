import os
from django.core.management.base import BaseCommand
import shopify
import requests
from studio.models import Item, SizeCategory, EcommerceStore


class Command(BaseCommand):
    help = 'Update item sizes based on Shopify and WooCommerce product availability'

    def handle(self, *args, **kwargs):
        # Filter items that are connected to an eCommerce store
        items = Item.objects.filter(
            ecommerce_store__isnull=False,  # Ensure there is an associated ecommerce store
            ecommerce_product_id__isnull=False  # Only items with a product ID
        )

        # Print the number of items found
        print(f"Found {items.count()} items to process.")

        if not items.exists():
            print("No items found matching the criteria.")
            return

        for item in items:
            ecommerce_store = item.ecommerce_store
            print(f"Processing Item ID: {item.id} - {item.name}")

            # Determine the platform and process accordingly
            if ecommerce_store.platform.lower() == 'shopify':
                self.process_shopify_item(item, ecommerce_store)
            elif ecommerce_store.platform.lower() == 'woocommerce':
                self.process_woocommerce_item(item, ecommerce_store)
            else:
                print(f"Unknown platform for Item ID: {item.id} - {ecommerce_store.platform}")

    def process_shopify_item(self, item, ecommerce_store):
        # Get Shopify credentials
        api_key = ecommerce_store.api_key
        api_secret = ecommerce_store.api_secret
        api_access_token = ecommerce_store.api_access_token
        shop_url = f"https://{ecommerce_store.shop_url}/admin"

        # Connect to Shopify
        shopify.ShopifyResource.set_site(shop_url)
        session = shopify.Session(shop_url, version="2023-04", token=api_access_token)
        shopify.ShopifyResource.activate_session(session)

        try:
            # Fetch Product from Shopify using the product ID
            print(f"Fetching product {item.ecommerce_product_id} from Shopify for Item ID: {item.id}")
            product = shopify.Product.find(item.ecommerce_product_id)
            available_sizes = []

            # Check availability of each size
            for variant in product.variants:
                size = variant.option1  # Assuming size is the first option
                availability = variant.inventory_quantity
                if availability > 0:
                    available_sizes.append(size)

            # Update sizes_xyz field in Item model
            if available_sizes:
                size_instances = SizeCategory.objects.filter(name__in=available_sizes)
                item.sizes_xyz.set(size_instances)
                item.save()
                self.stdout.write(self.style.SUCCESS(
                    f"Updated Item ID: {item.id} - Available Sizes: {', '.join(available_sizes)}"))
            else:
                item.sizes_xyz.clear()
                item.save()
                self.stdout.write(self.style.WARNING(f"Cleared sizes for Item ID: {item.id} - No sizes available"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error updating item {item.id} from Shopify: {e}"))

    def process_woocommerce_item(self, item, ecommerce_store):
        # Get WooCommerce credentials
        consumer_key = ecommerce_store.api_key
        consumer_secret = ecommerce_store.api_secret
        store_url = ecommerce_store.shop_url

        # WooCommerce API endpoint to fetch product data
        product_url = f"https://{store_url}/wp-json/wc/v3/products/{item.ecommerce_product_id}"

        print(f"Connecting to WooCommerce store: {store_url}")

        try:
            # Make a GET request to fetch the product data
            response = requests.get(product_url, auth=(consumer_key, consumer_secret))

            # If response is not successful, raise an exception
            if response.status_code != 200:
                print(f"Failed to fetch product {item.ecommerce_product_id}: {response.text}")
                return

            product = response.json()
            available_sizes = []

            # Check for variations in WooCommerce
            if 'variations' in product:
                # Fetch each variation's details
                for variation_id in product['variations']:
                    variation_url = f"https://{store_url}/wp-json/wc/v3/products/{item.ecommerce_product_id}/variations/{variation_id}"
                    variation_response = requests.get(variation_url, auth=(consumer_key, consumer_secret))

                    if variation_response.status_code != 200:
                        print(f"Failed to fetch variation {variation_id} for product {item.ecommerce_product_id}: {variation_response.text}")
                        continue

                    variation = variation_response.json()
                    size = variation.get('attributes', [{}])[0].get('option', None)  # Assuming size is the first attribute
                    availability = variation.get('stock_quantity', 0)

                    if size and availability > 0:
                        available_sizes.append(size)
            else:
                # No variations found, fallback to single product size if defined
                size = product.get('attributes', [{}])[0].get('option', None)
                availability = product.get('stock_quantity', 0)

                if size and availability > 0:
                    available_sizes.append(size)

            # Update sizes_xyz field in Item model
            if available_sizes:
                size_instances = SizeCategory.objects.filter(name__in=available_sizes)
                item.sizes_xyz.set(size_instances)
                item.save()
                print(f"Updated Item ID: {item.id} - Available Sizes: {', '.join(available_sizes)}")
            else:
                item.sizes_xyz.clear()
                item.save()
                print(f"Cleared sizes for Item ID: {item.id} - No sizes available")

        except Exception as e:
            print(f"Error updating item {item.id} from WooCommerce: {e}")