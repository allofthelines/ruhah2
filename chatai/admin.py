from django.contrib import admin
from .models import Product, ChatSession, ChatMessage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_name',
        'product_brand',
        'product_link',
        'product_price',
        'product_details',
        'product_created_at',
        'has_embedding',  # New computed field for list view
    )

    fields = (
        'product_name',
        'product_brand',
        'product_link',
        'product_images',
        'product_main_image',
        'product_price',
        'product_details',
        'product_created_at',
        'product_embedding',
    )

    readonly_fields = ('product_created_at', 'product_embedding',)

    # Optional: Add search and filtering for better admin usability
    search_fields = ('product_name', 'product_brand', 'product_details',)
    list_filter = ('product_brand', 'has_embedding',)  # Filter by brand and embedding status

    def has_embedding(self, obj):
        # Check if product_embedding exists and has length > 0 to avoid array truth value errors
        if obj.product_embedding and len(obj.product_embedding) > 0:
            return "Yes"
        return "No"

    has_embedding.short_description = "Has Embedding"  # Column header in admin
    has_embedding.boolean = True  # Displays as green check (Yes) or red cross (No)


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = (
        'chat_id',
        'chat_user',
        'chat_reference_item',
        'chat_reference_outfit_id',
        'chat_status',
        'chat_created_at',
    )

    fields = (
        'chat_id',
        'chat_user',
        'chat_reference_item',
        'chat_reference_outfit_id',
        'chat_status',
        'chat_created_at',
        'chat_main_embedding',  # Added to fields for visibility (was only in readonly_fields)
    )

    readonly_fields = ('chat_main_embedding', 'chat_created_at',)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = (
        'msg_chat_session',
        'msg_is_from_user',
        'msg_text',
        'msg_message_type',
        'msg_created_at',
    )

    fields = (
        'msg_chat_session',
        'msg_is_from_user',
        'msg_text',
        'msg_message_type',
        'msg_recommendations',
        'msg_image',
        'msg_image_url',
        'msg_created_at',
    )

    readonly_fields = ('msg_created_at',)