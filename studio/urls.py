from django.urls import path
from . import views
from .views import item_search

app_name = 'studio'

urlpatterns = [
    path('tickets/', views.studio_tickets, name='studio_tickets'),
    path('items/<int:ticket_id>/', views.studio_items, name='studio_items'),  # Assuming integer IDs for tickets
    path('items/guest/<int:ticket_id>/', views.studio_items_guest, name='studio_items_guest'),
    path('items/reset/<int:ticket_id>/<int:item_id>/', views.studio_items_reset, name='studio_items_reset'),
    path('item-search/<int:ticket_id>/', item_search, name='item_search'),
    path('add-item-to-temp/', views.add_item_to_temp, name='add_item_to_temp'),
    path('success/', views.studio_success, name='studio_success'),
    path('submit_outfit/<int:ticket_id>/', views.submit_outfit, name='submit_outfit'),
]