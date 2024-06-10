#!/usr/bin/env python3

import os
from django.core.management.base import BaseCommand
import shopify
from studio.models import Item

class Command(BaseCommand):
    help = 'Update item sizes based on Shopify product availability'
    
    def handle(self, *args, **kwargs):
        items = Item.objects.filter(shopify_store__isnull=False, shopify_product_id__isnull=False)
        
        for item in items:
            shopify_store = item.shopify_store
            api_key = shopify_store.api_key
            api_secret = shopify_store.api_secret
            access_token = shopify_store.access_token
            shop_url = f"https://{api_key}:{api_secret}@{shopify_store.shop_url}/admin"
            
            shopify.ShopifyResource.set_site(shop_url)
            session = shopify.Session(shop_url, version="2023-04", token=access_token)
            shopify.ShopifyResource.activate_session(session)
            
            try:
                # Fetch Product from Shopify using the product ID
                product = shopify.Product.find(item.shopify_product_id)
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
                    self.stdout.write(self.style.SUCCESS(f"Updated Item ID: {item.id} - Available Sizes: {', '.join(available_sizes)}"))
                else:
                    item.sizes_xyz.clear()
                    item.save()
                    self.stdout.write(self.style.WARNING(f"Cleared sizes for Item ID: {item.id} - No sizes available"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error updating item {item.id}: {e}"))
                