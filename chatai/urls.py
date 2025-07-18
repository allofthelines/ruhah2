from django.urls import path
from . import views

app_name = 'chatai'

urlpatterns = [
    path('aichat/', views.AIChatStartView.as_view(), name='start_aichat'),  # Starter for button
    path('aichat/<str:chat_id>/', views.AIChatView.as_view(), name='aichat'),
]
]