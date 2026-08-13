from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('verification.urls')),
    path('accounts/', include('accounts.urls')),
    path('certificates/', include('certificates.urls')),
]

handler400 = 'config.views.custom_bad_request'
handler403 = 'config.views.custom_permission_denied'
handler404 = 'config.views.custom_page_not_found'
handler500 = 'config.views.custom_server_error'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
