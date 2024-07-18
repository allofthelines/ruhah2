from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

print('\n\n\n DEBUG VIEWS DEBUG VIEWS DEBUG VIEWS\n\n\n')

urlpatterns = [

    path('remove_ask/<int:ticket_id>/', views.remove_ask, name='remove_ask'),

    path('remove_outfit/<int:outfit_id>/', views.remove_outfit, name='remove_outfit'),

    path('like-outfit/', views.like_outfit, name='like_outfit'),
    path('remove-like/<int:like_id>/', views.remove_like, name='remove_like'),

    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html', next_page='core:home'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('upload_success/', views.upload_success, name='upload_success'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('activation_success/', views.activation_success, name='activation_success'),
    path('account_activation_sent/', views.account_activation_sent, name='account_activation_sent'),

    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),

    path('<str:username>/', views.public_profile, name='public_profile'),
    path('follow/<str:username>/', views.follow, name='follow'),
    path('unfollow/<str:username>/', views.unfollow, name='unfollow'),
    path('<str:username>/followers/', views.followers_list, name='followers_list'),
    path('<str:username>/following/', views.following_list, name='following_list'),

    path('change-email/', views.email_change_request, name='change_email'),
    path('email-change-requested/', views.email_change_requested, name='email_change_requested'),
    path('confirm-email/<str:uidb64>/<str:token>/', views.confirm_email, name='confirm_email'),
]
