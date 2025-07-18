from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Min
from .models import Outfit
from box.models import Ticket
from django.utils import timezone

# einai helper etsi wste na einai ordered to list_filter me ta ticketid twn outfits swsta (3->2->1)
# thelw ta megala na einai panw panw giati einai ta pio prosfata tickets
# tha xrhsimopoieitai syxna gia na apomonwnw ta outfit enos ticket mono
class SortedTicketListFilter(admin.SimpleListFilter):
    title = 'Ticket ID'
    parameter_name = 'ticket_id'

    def lookups(self, request, model_admin):
        ticket_ids = Outfit.objects.values_list('ticket_id__id', flat=True).distinct().order_by('-ticket_id__id')
        return [(str(tid), f'Ticket {tid}') for tid in ticket_ids if tid is not None]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(ticket_id__id=self.value())
        return queryset

class OutfitAdmin(admin.ModelAdmin):
    list_display = ('id', 'thumbnail', 'maker_id', 'maker_grid', 'image', 'rating', 'ticket_id', 'portrait_thumbnail', 'days_since_creation')
    list_filter = (SortedTicketListFilter,)
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

    def days_since_creation(self, obj):
        if obj.timestamp:
            days = (timezone.now() - obj.timestamp).days
            return f"{days} day{'s' if days != 1 else ''}"
        return "N/A"
    days_since_creation.short_description = 'Age (days)'

    # Customizing the formfield for ticket_id
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'ticket_id':
            kwargs['queryset'] = Ticket.objects.order_by('pk')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Register the Outfit model with the OutfitAdmin options
admin.site.register(Outfit, OutfitAdmin)