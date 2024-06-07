import os
from django.core.management.base import BaseCommand
import shopify

class Command(BaseCommand):
    help = 'Test Shopify API connection'

    def handle(self, *args, **kwargs):
        api_key = os.getenv('SHOPIFY_API_KEY_DEV')
        api_secret = os.getenv('SHOPIFY_API_SECRET_DEV')
        access_token = os.getenv('SHOPIFY_ACCESS_TOKEN_DEV')
        shop_url = f"https://{api_key}:{api_secret}@fumioxyz.myshopify.com/admin"

        shopify.ShopifyResource.set_site(shop_url)
        session = shopify.Session(shop_url, version="2023-04", token=access_token)
        shopify.ShopifyResource.activate_session(session)

        # Example: Fetch Products
        products = shopify.Product.find()
        for product in products:
            self.stdout.write(self.style.SUCCESS(f"Product: {product.title}"))
