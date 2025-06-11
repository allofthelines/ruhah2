import os
from django.core.management.base import BaseCommand
import shopify
from studio.models import Item, EcommerceStore


class Command(BaseCommand):
    help = 'Update item name and price based on Shopify product data'

    def handle(self, *args, **kwargs):
        # Filter items that are connected to a Shopify store and have relevant categories
        items = Item.objects.filter(
            ecommerce_store__platform='shopify',
            ecommerce_product_id__isnull=False,
            cat__in=['dress', 'top', 'bottom', 'accessory']
        )

        for item in items:
            ecommerce_store = item.ecommerce_store

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
                # Fetch product from Shopify
                self.stdout.write(self.style.NOTICE(f"Fetching product {item.ecommerce_product_id} for Item ID: {item.id}"))
                product = shopify.Product.find(item.ecommerce_product_id)

                if not product:
                    self.stdout.write(self.style.WARNING(f"No product found for Item ID: {item.id}"))
                    continue

                # Update item name and price
                item.name = product.title
                max_price = max(float(variant.price) for variant in product.variants)
                item.price = max_price
                item.save()

                self.stdout.write(self.style.SUCCESS(
                    f"Updated Item ID: {item.id} - Name: {product.title}, Price: {max_price}"
                ))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error updating item {item.id}: {e}"))