from django.contrib import admin
from .models import Product, ChatSession, ChatMessage


# @admin.register(Product)
from django.db.models import Q
from django.contrib.postgres.search import SearchVector

# @admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_name',
        'product_images',
        'product_brand',
        'product_link',
        'product_price',
        'product_details',
        'product_created_at',
    )

    fields = (
        'product_name',
        'product_brand',
        'product_category',
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
    search_fields = (
    'product_name', 'product_brand', 'product_details')  # Removed product_images from here; we'll handle it custom

    list_filter = ('product_brand',)  # Filter by brand and embedding status

    def get_search_results(self, request, queryset, search_term):
        """
        Custom search to include text search inside product_images JSON as if it's a string.
        """
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if search_term:
            # Search in other fields as usual (from search_fields)
            # Now add custom search for product_images: treat it as text
            vector = SearchVector('product_images',
                                  config='english')  # Assuming PostgreSQL; convert JSON to text for search
            queryset = queryset.annotate(search=vector).filter(search=search_term) | queryset

            # Alternatively, if not using SearchVector, a simple icontains on cast to str (but SearchVector is better for Postgres)
            # queryset = queryset.filter(product_images__icontains=search_term)  # This works if JSONField is searchable as text

        return queryset, use_distinct



admin.site.register(Product, ProductAdmin)

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