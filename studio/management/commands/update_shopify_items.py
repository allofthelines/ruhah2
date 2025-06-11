import os
from django.core.management.base import BaseCommand
import shopify
import requests
from requests.exceptions import SSLError
from studio.models import Item, EcommerceStore


class Command(BaseCommand):
    help = 'Update item name and price based on Shopify or WooCommerce product data'

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

        # Print Shopify credentials (masked for security)
        print(f"Connecting to Shopify store: {shop_url}")

        # Connect to Shopify
        shopify.ShopifyResource.set_site(shop_url)
        session = shopify.Session(shop_url, version="2023-04", token=api_access_token)
        shopify.ShopifyResource.activate_session(session)

        try:
            # Fetch product from Shopify
            print(f"Fetching product {item.ecommerce_product_id} for Item ID: {item.id}")
            product = shopify.Product.find(item.ecommerce_product_id)

            if not product:
                print(f"No product found for Item ID: {item.id}")
                return

            # Update item name and price
            item.name = product.title
            print(f"Product title from Shopify: {product.title}")

            # Find the highest price among variants
            max_price = max(float(variant.price) for variant in product.variants)
            print(f"Highest variant price from Shopify: {max_price}")

            item.price = max_price
            item.save()

            print(f"Updated Item ID: {item.id} - Name: {item.name}, Price: {item.price}")

        except Exception as e:
            print(f"Error updating item {item.id}: {e}")

        print('')

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
            response = requests.get(product_url, auth=(consumer_key, consumer_secret), verify=False)

            # If response is not successful, raise an exception
            if response.status_code != 200:
                print(f"Failed to fetch product {item.ecommerce_product_id}: {response.text}")
                return

            product = response.json()

            # Update item name
            item.name = product.get('name', 'Unnamed Product')
            print(f"Product title from WooCommerce: {item.name}")

            # Try to get the first price available
            price = product.get('price', None)  # Get the main product price
            if not price:  # If no main product price, check the variations
                variations = product.get('variations', [])
                if isinstance(variations, list) and variations:
                    price = float(variations[0].get('price', 0))  # Take the first variation's price

            if not price:
                print(f"No price found for Item ID: {item.id}")
                return

            print(f"Price from WooCommerce: {price}")

            item.price = price
            item.save()

            print(f"Updated Item ID: {item.id} - Name: {item.name}, Price: {item.price}")

        except Exception as e:
            print(f"Error updating item {item.id}: {e}")

        print('')  # Empty line for readability