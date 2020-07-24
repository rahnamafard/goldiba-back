from django.urls import path, include
from rest_framework.routers import DefaultRouter

# from .views import RecipeViewSet
from core import views

router = DefaultRouter()
# router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("request-verification/", views.RequestVerificationCodeAPIView.as_view(), name='request verification'),
    path("verify-phone/" , views.VerifyMobileNumberAPIView.as_view(), name='verify phone'),
    path('register-user/', views.CreateUserAPIView.as_view(), name='register user'),
]