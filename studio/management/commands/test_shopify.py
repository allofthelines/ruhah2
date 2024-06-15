'''
import os
from django.core.management.base import BaseCommand
import shopify

class Command(BaseCommand):
    help = 'Test Shopify API connection'

    def handle(self, *args, **kwargs):
        api_key = os.getenv('SHOPIFY_API_KEY_DEV')
        api_secret = os.getenv('SHOPIFY_API_SECRET_DEV')
        api_access_token = os.getenv('SHOPIFY_ACCESS_TOKEN_DEV')
        shop_url = f"https://{api_key}:{api_secret}@fumioxyz.myshopify.com/admin"

        shopify.ShopifyResource.set_site(shop_url)
        session = shopify.Session(shop_url, version="2023-04", token=api_access_token)
        shopify.ShopifyResource.activate_session(session)

        # Fetch Products from Shopify
        products = shopify.Product.find()
        for product in products:
            title = product.title
            availability = sum(variant.inventory_quantity for variant in product.variants)
            self.stdout.write(self.style.SUCCESS(f"Product: {title}, Availability: {availability}"))
'''
            
import os
from django.core.management.base import BaseCommand
import shopify

class Command(BaseCommand):
    help = 'Test Shopify API connection and display product details'
    
    def handle(self, *args, **kwargs):
        api_key = os.getenv('SHOPIFY_API_KEY_DEV')
        api_secret = os.getenv('SHOPIFY_API_SECRET_DEV')
        api_access_token = os.getenv('SHOPIFY_ACCESS_TOKEN_DEV')
        
        if not all([api_key, api_secret, api_access_token]):
            self.stderr.write(self.style.ERROR('One or more Shopify API credentials are missing.'))
            return
        
        shop_url = f"https://{api_key}:{api_secret}@fumioxyz.myshopify.com/admin"
        shopify.ShopifyResource.set_site(shop_url)
        session = shopify.Session(shop_url, version="2023-04", token=api_access_token)
        shopify.ShopifyResource.activate_session(session)
        
        try:
            # Fetch Products from Shopify
            products = shopify.Product.find()
            for product in products:
                title = product.title
                primary_key = product.id  # Fetching the primary key (Shopify product ID)
                self.stdout.write(self.style.SUCCESS(f"Product ID: {primary_key} - {title}"))
                
                # Display the availability and price of each size
                for variant in product.variants:
                    size = variant.option1  # Assuming size is the first option
                    availability = variant.inventory_quantity
                    price = variant.price  # Fetching the price
                    self.stdout.write(self.style.SUCCESS(f"  {title}, {size}, Availability: {availability}, Price: {price}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error fetching products: {e}"))
            