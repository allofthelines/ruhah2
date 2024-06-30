from django.urls import path
from .views import ticket_view, success_view, api_tickets
from .views import ticket_view, success_view, api_tickets, stripe_webhook, create_checkout_session
from .views import payment_successful, payment_rejected
from .views import ask_fit_view, ask_box_view, ask_fit_success, success_view

urlpatterns = [
    path('ticket/', ticket_view, name='ticket_form'),
    path('ticket/success/', success_view, name='success_url'),
    path('api/tickets/', api_tickets, name='api-tickets'),
    path('webhook/stripe/', stripe_webhook, name='stripe-webhook'),
    path('create-checkout-session/<int:ticket_id>/', create_checkout_session, name='create-checkout-session'),
    path('payment-successful/', payment_successful, name='payment_successful'),
    path('payment-rejected/', payment_rejected, name='payment_rejected'),

    path('ask/fit/', views.ask_fit_view, name='ask_fit'),
    path('ask/box/', views.ask_box_view, name='ask_box'),
    path('ask/fit/success/<int:ticket_id>/', views.ask_fit_success, name='ask_fit_success'),
    path('success/<int:ticket_id>/', views.success_view, name='success'),
]