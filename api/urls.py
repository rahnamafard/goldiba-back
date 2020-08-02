from django.contrib import admin
from django.urls import include, path
from django.conf import settings             # for settings.DEBUG
from django.conf.urls.static import static   # static

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.views import MyTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),

    # path("api/token/", TokenObtainPairView.as_view(), name="token"),
    path('api/token/', MyTokenObtainPairView.as_view(), name='custom jwt token'),
    path("api/refresh_token/", TokenRefreshView.as_view(), name="refresh token"),
]

# adding media to urls
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)