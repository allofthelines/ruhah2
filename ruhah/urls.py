from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # This line adds the admin interface
    path('box/', include(('box.urls', 'box'), namespace='box')),
    path('accounts/', include('accounts.urls', namespace='accounts')),  # Include with namespace
    path('studio/', include('studio.urls', namespace='studio')),
    path('chatai/', include('chatai.urls', namespace='chatai')),
    path("", include("core.urls")),
    path('', include('pwa.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Ensure static files are served correctly (useful during development)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
