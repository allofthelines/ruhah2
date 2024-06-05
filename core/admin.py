from django.contrib import admin
from django.utils.html import format_html
from .models import Outfit

class OutfitAdmin(admin.ModelAdmin):
    list_display = ('id', 'thumbnail', 'maker_id', 'image', 'rating', 'ticket_id')
    list_filter = ('ticket_id',)
    search_fields = ('rating', 'id', 'ticket_id__id', 'maker_id__username')  # Adjust based on the actual fields

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px;" />', obj.image.url)
        return ""
    thumbnail.short_description = 'Image'

# Register the Outfit model with the OutfitAdmin options
admin.site.register(Outfit, OutfitAdmin)