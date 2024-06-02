from django.urls import path

from . import views

app_name = "core"
urlpatterns = [
    path("", views.home, name="home"),
    path("upload/", views.UploadView.as_view(), name="upload"),
    path("trending/", views.TrendingView.as_view(), name="trending"),
    path("terms/", views.TermsView.as_view(), name="terms"),
    path("privacy/", views.PrivacyView.as_view(), name="privacy"),
    path("help/", views.HelpView.as_view(), name="help"),
    path("social/", views.SocialView.as_view(), name="social"),
    path('search/', views.search, name='search'),
]
