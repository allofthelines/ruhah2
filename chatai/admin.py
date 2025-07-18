from django.contrib import admin
from .models import Product, ChatSession, ChatMessage

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_brand', 'product_link', 'product_price', 'product_details', 'product_created_at')  # Columns in list view

    fields = ('product_name', 'product_brand', 'product_link', 'product_images', 'product_main_image' 'product_price', 'product_details')  # Editable in detail view (JSON as text)
    readonly_fields = ('product_created_at', 'product_embedding',)  # Auto-field non-editable

class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'chat_user', 'chat_reference_item', 'chat_reference_outfit_id', 'chat_status')
    
    fields = ('chat_id', 'chat_user', 'chat_reference_item', 'chat_reference_outfit_id', 'chat_status')
    readonly_fields = ('chat_main_embedding', 'chat_created_at')