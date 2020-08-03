from django.contrib import admin
from django.urls import include, path
from django.conf import settings             # for settings.DEBUG
from django.conf.urls.static import static   # static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
]

# adding media to urls
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)