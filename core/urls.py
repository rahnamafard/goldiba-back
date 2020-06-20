from django.urls import path, include
from rest_framework.routers import DefaultRouter

# from .views import RecipeViewSet
from core import views

router = DefaultRouter()
# router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("request-verification/", views.request_send_verify_sms, name='request verification'),
    path("verify-phone/", views.verify_mobile_number, name='verify phone'),
]