from django.contrib import admin
from .models import Ticket, Order, Return
from core.models import Outfit
from django.utils import timezone

# Register your models here.
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    # se list_display        , 'stylist_type'
    list_display = ['id', 'asktype', 'stylist_type', 'status', 'creator_id', 'short_notes', 'outfit1', 'outfit2', 'occupancy', 'days_since_creation']
    list_filter = ['asktype', 'status', 'occasion', 'style1', 'style2', 'boxcuratedby']
    search_fields = ['notes']

    def short_notes(self, obj):
        if obj.notes:
            return obj.notes[:25] + '...' if len(obj.notes) > 25 else obj.notes
        return ""

    def occupancy(self, obj):
        return f"{obj.current_outfits} / {obj.maximum_outfits}"
    occupancy.short_description = 'Occupancy'

    def days_since_creation(self, obj):
        if obj.timestamp:
            days = (timezone.now() - obj.timestamp).days
            return f"{days} day{'s' if days != 1 else ''}"
        return "N/A"
    days_since_creation.short_description = 'Age (days)'

    # Customizing the formfield for outfit1 and outfit2
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'outfit1' or db_field.name == 'outfit2':
            kwargs['queryset'] = Outfit.objects.order_by('pk')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    short_notes.short_description = 'Notes'

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'ticket_id', 'status', 'timestamp', 'hours_preparing')
    list_filter = ('status', 'type')
    ordering = ['timestamp']
    readonly_fields = ('hours_preparing',)  # Show hours_preparing in the detail view

    # Optional: Allow sorting by hours_preparing
    def get_ordering(self, request):
        return ['timestamp']

admin.site.register(Order, OrderAdmin)
admin.site.register(Return)