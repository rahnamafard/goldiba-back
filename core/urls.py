from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import views

router = DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),

    # Authentication
    path("request-verification/", views.RequestVerificationCodeAPIView.as_view(), name='request verification'),
    path("verify-phone/" , views.VerifyMobileNumberAPIView.as_view(), name='verify phone'),
    path('register-user/', views.CreateUserAPIView.as_view(), name='register user'),
    path('auth/logout/', views.LogoutAPIVIew.as_view(), name='logout user'),

    # Reset Password
    path('user/request-reset-password-code/', views.RequestResetPasswordCodeAPIView.as_view(), name='request reset pass'),
    path('user/verify-reset-password-code/', views.VerifyResetPasswordCodeAPIView.as_view(), name='verify reset pass'),
    path('user/reset-password', views.ResetPasswordAPIView.as_view(), name='change pass'),
]