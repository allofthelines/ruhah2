from django.contrib import admin
from .models import Ticket, Order, Return
from core.models import Outfit

# Register your models here.
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Ticket._meta.get_fields()]
    list_display = ['id', 'asktype', 'status', 'creator_id', 'short_notes', 'outfit1', 'outfit2', 'occupancy']
    list_filter = ['asktype', 'status', 'occasion', 'style1', 'style2', 'boxcuratedby']
    search_fields = ['notes']

    def short_notes(self, obj):
        if obj.notes:
            return obj.notes[:25] + '...' if len(obj.notes) > 25 else obj.notes
        return ""

    def occupancy(self, obj):
        return f"{obj.current_outfits} / {obj.maximum_outfits}"
    occupancy.short_description = 'Occupancy'

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