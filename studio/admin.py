from django.contrib import admin
from .models import Item, Tag, StudioOutfitTemp, ShopifyStore
from django.utils.html import format_html

# Register your models here.
class ItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'itemid', 'owner', 'thumbnail', 'image', 'size_xyz', 'sizes_xyz', 'is_ship_ready']
    search_fields = ['name', 'brand', 'itemid', 'location', 'tags']
    list_filter = ['condition', 'is_ship_ready', 'location', 'size_xyz', 'cat']
    ordering = ['itemid']
    fields = ['itemid', 'name', 'cat', 'brand', 'owner', 'condition',
              'location', 'is_ship_ready', 'tags', 'taglist', 'image',
              'size_xyz', 'sizes_xyz', 'shopify_store', 'shopify_product_id', 'price']

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 40px; height: 40px;" />', obj.image.url)
        return ""
    thumbnail.short_description = 'Image'

    def display_tags(self, obj):
        return ", ".join([tag.tag_name for tag in obj.tags.all()])

admin.site.register(Item, ItemAdmin)



class StudioOutfitTempAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticket', 'user']
    search_fields = ['ticket', 'user']
    list_filter = ['ticket', 'user']
    ordering = ['ticket']
    fields = ['ticket', 'user', 'item1img', 'item1id', 'item2img', 'item2id', 'item3img', 'item3id', 'item4img', 'item4id']

admin.site.register(StudioOutfitTemp, StudioOutfitTempAdmin)



class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'tag_name', 'tag_type']
    search_fields = ['tag_name', 'tag_type']
    list_filter = ['tag_type']
    ordering = ['tag_type']
    fields = ['id', 'tag_name', 'tag_type']

admin.site.register(Tag, TagAdmin)

class ShopifyStoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'shop_url', 'api_key', 'api_secret', 'access_token')
    search_fields = ('name', 'shop_url')
    readonly_fields = ('size_mapping',)

admin.site.register(ShopifyStore, ShopifyStoreAdmin)