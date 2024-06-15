import os
from django.core.management.base import BaseCommand
import shopify
from studio.models import Item, SizeCategory, EcommerceStore


class Command(BaseCommand):
    help = 'Update item sizes based on Shopify product availability'

    def handle(self, *args, **kwargs):
        items = Item.objects.filter(ecommerce_store__isnull=False, ecommerce_product_id__isnull=False)

        for item in items:
            ecommerce_store = item.ecommerce_store  # This is the foreign key relationship

            if ecommerce_store.platform != 'shopify':
                continue

            api_key = ecommerce_store.api_key
            api_secret = ecommerce_store.api_secret
            api_access_token = ecommerce_store.api_access_token
            shop_url = f"https://{api_key}:{api_secret}@fumioxyz.myshopify.com/admin"
            # shop_url = f"https://{api_key}:{api_secret}@{ecommerce_store.shop_url}/admin"

            shopify.ShopifyResource.set_site(shop_url)
            session = shopify.Session(shop_url, version="2023-04", token=api_access_token)
            shopify.ShopifyResource.activate_session(session)

            try:
                # Fetch Product from Shopify using the product ID
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
                self.stderr.write(self.style.ERROR(f"Error updating item {item.id}: {e}"))
