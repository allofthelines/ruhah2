from django.contrib import admin
from django.utils.html import format_html
from .models import Outfit

class OutfitAdmin(admin.ModelAdmin):
    list_display = ('id', 'thumbnail', 'maker_id', 'maker_grid', 'image', 'rating', 'ticket_id', 'portrait_thumbnail')
    list_filter = ('ticket_id',)
    search_fields = ('rating', 'id', 'ticket_id__id', 'maker_id__username')  # Adjust based on the actual fields

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px;" />', obj.image.url)
        return ""
    thumbnail.short_description = 'Image'

    def portrait_thumbnail(self, obj):
        if obj.portrait:
            return format_html('<img src="{}" style="width: 50px; height: 50px;" />', obj.portrait.url)
        return ""

    def maker_grid(self, obj):
        return obj.maker_grid_visibility
    maker_grid.short_description = 'Maker Grid'

    portrait_thumbnail.short_description = 'Portrait'


# Register the Outfit model with the OutfitAdmin options
admin.site.register(Outfit, OutfitAdmin)