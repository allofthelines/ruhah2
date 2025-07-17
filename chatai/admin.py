from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_brand', 'product_link', 'product_price', 'product_details', 'product_created_at')  # Columns in list view
    fields = ('product_name', 'product_brand', 'product_link', 'product_images', 'product_main_image' 'product_price', 'product_details')  # Editable in detail view (JSON as text)
    readonly_fields = ('product_created_at', 'product_embedding',)  # Auto-field non-editable