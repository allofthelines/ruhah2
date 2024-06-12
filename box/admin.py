from django.contrib import admin
from .models import Ticket, Order, Return

# Register your models here.
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Ticket._meta.get_fields()]
    list_display = ['id', 'status', 'creator_id', 'notes', 'outfit1', 'outfit2']
    list_filter = ['status', 'occasion', 'style1', 'style2']

    def short_notes(self, obj):
        if obj.notes:
            return obj.notes[:15] + '...' if len(obj.notes) > 15 else obj.notes
        return ""

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