from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

print('\n\n\n DEBUG VIEWS DEBUG VIEWS DEBUG VIEWS\n\n\n')

urlpatterns = [

    path('remove_ask/<int:ticket_id>/', views.remove_ask, name='remove_ask'),

    path('remove_outfit/<int:outfit_id>/', views.remove_outfit, name='remove_outfit'),

    path('remove_gridpic/<int:gridpic_id>/', views.remove_gridpic, name='remove_gridpic'),

    path('like-outfit/', views.like_outfit, name='like_outfit'),
    path('remove-like/<int:like_id>/', views.remove_like, name='remove_like'),
    path('remove-all-likes/', views.remove_all_likes, name='remove_all_likes'),

    path('profile/ask_outfit_details/<int:outfit_id>/', views.profile_ask_outfit_details, name='profile_ask_outfit_details'),
    path('profile/likes/randomize/', views.profile_likes_randomize, name='profile_likes_randomize'),

    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html', next_page='core:home'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('upload_success/', views.upload_success, name='upload_success'),
    path('upload_gridpic_success/', views.upload_gridpic_success, name='upload_gridpic_success'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('activation_success/', views.activation_success, name='activation_success'),
    path('account_activation_sent/', views.account_activation_sent, name='account_activation_sent'),

    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),

    path('change-email/', views.email_change_request, name='change_email'),
    path('email-change-requested/', views.email_change_requested, name='email_change_requested'),
    path('confirm-email/<str:uidb64>/<str:token>/', views.confirm_email, name='confirm_email'),

    path('<str:username>/', views.public_profile, name='public_profile'),
    path('follow/<str:username>/', views.follow, name='follow'),
    path('unfollow/<str:username>/', views.unfollow, name='unfollow'),
    path('<str:username>/followers/', views.followers_list, name='followers_list'),
    path('<str:username>/following/', views.following_list, name='following_list'),

    path('gridpic/<int:gridpic_id>/try-on/', views.profile_gridpic_try_on, name='profile_gridpic_try_on'),
    path('gridpic/<int:gridpic_id>/perform-try-on/<int:item_id>/', views.perform_try_on, name='perform_try_on'),
    path('gridpic/<int:gridpic_id>/accept-temp/', views.accept_temp_image, name='accept_temp_image'),
    path('gridpic/<int:gridpic_id>/reject-temp/', views.reject_temp_image, name='reject_temp_image'),
    path('try-on/submitted/', views.profile_try_on_submitted, name='profile_try_on_submitted'),
    path('gridpic/<int:gridpic_id>/delete-all-tryons/', views.delete_all_tryons, name='delete_all_tryons'),

    path('tryon-item-search/<int:gridpic_id>/', views.tryon_item_search, name='tryon_item_search'),

]