from django.urls import path
from . import views

urlpatterns = [
    path('start-aichat/', views.AIChatStartView.as_view(), name='start_aichat'),  # Starter for button
    path('aichat/', views.AIChatView.as_view(), name='aichat'),  # Main clean URL
]