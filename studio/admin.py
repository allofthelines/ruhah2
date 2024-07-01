from django.contrib import admin
from .models import Item, Tag, StudioOutfitTemp, EcommerceStore, SizeCategory, SizeShoeUkCategory, SizeWaistInchCategory
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from .forms import EcommerceStoreForm
from django import forms

class SizesFilter(SimpleListFilter):
    title = 'sizes'
    parameter_name = 'sizes_xyz'

    def lookups(self, request, model_admin):
        sizes = SizeCategory.objects.all()
        return [(size.id, size.name) for size in sizes]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(sizes_xyz__id__exact=self.value())
        return queryset

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = '__all__'
        widgets = {
            'tags': forms.Textarea(attrs={'rows': 3}),
        }

class ItemAdmin(admin.ModelAdmin):
    form = ItemForm
    list_display = ['id', 'itemid', 'thumbnail', 'image', 'modality', 'ecommerce_store']
    search_fields = ['name', 'itemid', 'location', 'tags']
    list_filter = [SizesFilter, 'condition', 'location', 'cat', 'modality', 'ecommerce_store']
    ordering = ['itemid']
    fields = [
        'image', 'itemid', 'tags',
        'ecommerce_product_id', 'ecommerce_store', 'modality', 'cat', 'taglist', 'condition',
        'name', 'price', 'sizes_xyz', 'sizes_shoe_uk', 'sizes_shoe_eu', 'sizes_waist_inches',
        'location'
    ]

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 40px; height: 40px;" />', obj.image.url)
        return ""
    thumbnail.short_description = 'Image'

    def display_sizes(self, obj):
        return ", ".join([size.name for size in obj.sizes_xyz.all()])
    display_sizes.short_description = 'Sizes'

    def display_tags(self, obj):
        return ", ".join([tag.tag_name for tag in obj.taglist.all()])

admin.site.register(Item, ItemAdmin)



class StudioOutfitTempAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticket', 'user']
    search_fields = ['ticket', 'user']
    list_filter = ['ticket', 'user']
    ordering = ['ticket']
    fields = ['ticket', 'user', 'item1img', 'item1id', 'item2img', 'item2id', 'item3img', 'item3id', 'item4img', 'item4id']

admin.site.register(StudioOutfitTemp, StudioOutfitTempAdmin)



class TagAdmin(admin.ModelAdmin):
    list_display = ['tag_name', 'tag_type']
    search_fields = ['tag_name', 'tag_type']
    list_filter = ['tag_type']
    ordering = ['tag_type']
    fields = ['tag_name', 'tag_type']

admin.site.register(Tag, TagAdmin)

class EcommerceStoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'shop_url', 'platform', 'api_key', 'api_secret', 'api_access_token')
    search_fields = ('name', 'shop_url')

    form = EcommerceStoreForm

admin.site.register(EcommerceStore, EcommerceStoreAdmin)