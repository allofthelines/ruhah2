from django.contrib import admin
from .models import Product, ChatSession, ChatMessage

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_brand', 'product_link', 'product_price', 'product_details', 'product_created_at')  # Columns in list view

    fields = ('product_name', 'product_brand', 'product_link', 'product_images', 'product_main_image', 'product_price', 'product_details', 'product_created_at', 'product_embedding')  # Editable in detail view (JSON as text)
    readonly_fields = ('product_created_at', 'product_embedding',)  # Auto-field non-editable

class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'chat_user', 'chat_reference_item', 'chat_reference_outfit_id', 'chat_status', 'chat_created_at')

    fields = ('chat_id', 'chat_user', 'chat_reference_item', 'chat_reference_outfit_id', 'chat_status', 'chat_created_at', 'chat_created_at')
    readonly_fields = ('chat_main_embedding', 'chat_created_at')

admin.site.register(ChatSession, ChatSessionAdmin)

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('msg_chat_session', 'msg_is_from_user', 'msg_text', 'msg_message_type', 'msg_created_at')

    fields = ('msg_chat_session', 'msg_is_from_user', 'msg_text', 'msg_message_type', 'msg_recommendations', 'msg_image', 'msg_image_url', 'msg_created_at')
    readonly_fields = ('msg_created_at',)

admin.site.register(ChatMessage, ChatMessageAdmin)