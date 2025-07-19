from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from django.utils.html import format_html
from .models import Product, ChatSession, ChatMessage


class HasEmbeddingFilter(SimpleListFilter):
    title = 'Has Embedding'
    parameter_name = 'has_embedding'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(product_embedding__isnull=True).exclude(product_embedding__len=0)
        if self.value() == 'no':
            return queryset.filter(product_embedding__isnull=True) | queryset.filter(product_embedding__len=0)
        return queryset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_name',
        'product_brand',
        'product_link',
        'product_price',
        'product_details',
        'product_created_at',
        'has_embedding',
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

    search_fields = ('product_name', 'product_brand', 'product_details',)

    list_filter = ('product_brand', HasEmbeddingFilter,)

    def has_embedding(self, obj):
        if obj.product_embedding and len(obj.product_embedding) > 0:
            return "Yes"
        return "No"

    has_embedding.short_description = "Has Embedding"
    has_embedding.boolean = True


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
        'chat_main_embedding',
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