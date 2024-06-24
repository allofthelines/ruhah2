import os
from django.core.management.base import BaseCommand
import shopify
from studio.models import EcommerceStore

class Command(BaseCommand):
    help = 'Test Shopify API connection and display product details'

    def handle(self, *args, **kwargs):
        ecommerce_stores = EcommerceStore.objects.filter(platform='shopify')

        for ecommerce_store in ecommerce_stores:
            api_key = ecommerce_store.api_key
            api_secret = ecommerce_store.api_secret
            api_access_token = ecommerce_store.api_access_token
            api_store_id = ecommerce_store.api_store_id

            shop_url = f"https://{api_key}:{api_secret}@{api_store_id}.myshopify.com/admin"
            shopify.ShopifyResource.set_site(shop_url)
            session = shopify.Session(shop_url, version="2023-04", token=api_access_token)
            shopify.ShopifyResource.activate_session(session)

            try:
                # Fetch all Products from Shopify
                products = shopify.Product.find()
                for product in products:
                    self.stdout.write(self.style.SUCCESS(f"Product ID: {product.id} - {product.title}"))

                    # Display the availability and price of each size
                    for variant in product.variants:
                        size = variant.option1  # Assuming size is the first option
                        availability = variant.inventory_quantity
                        price = variant.price  # Fetching the price
                        self.stdout.write(self.style.SUCCESS(
                            f"  {product.title}, {size}, Availability: {availability}, Price: {price}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error fetching products from store {ecommerce_store.name}: {e}"))
