from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import views

router = DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),

    # Authentication
    path('auth/login/', views.LoginAPIView.as_view(), name='login user'),
    path('auth/logout/', views.LogoutAPIVIew.as_view(), name='logout user'),
    path("request-verification/", views.RequestVerificationCodeAPIView.as_view(), name='request verification'),
    path("verify-phone/" , views.VerifyMobileNumberAPIView.as_view(), name='verify phone'),
    path('register-user/', views.CreateUserAPIView.as_view(), name='register user'),

    # Reset Password
    path('user/request-reset-password-code/', views.RequestResetPasswordCodeAPIView.as_view(), name='request reset pass'),
    path('user/verify-reset-password-code/', views.VerifyResetPasswordCodeAPIView.as_view(), name='verify reset pass'),
    path('user/reset-password', views.ResetPasswordAPIView.as_view(), name='change pass'),

    # User Info
    path('auth/user/', views.UserMetaDataAPIVIew.as_view(), name='user meta data'),

    # Product
    path('product/new-product-form-info/', views.NewProductFormInfoAPIView.as_view(), name="new product form info"),
    url(r'^product/$', views.ProductAPIView.as_view(), name="product api"),

    # Tag
    # path('tag/create-if-not-exists/', views.CreateTagIfNotExists.as_view(), name="create tag if not exists"),

    # Model
    path('product/model/', views.ModelAPIView.as_view(), name="model api"),

    # Color
    path('color/', views.ColorAPIView.as_view(), name="color api"),

    # Product Category (Order of urls is important!)
    url('^category/parent(?:/(?P<id>.+))?/$', views.CategoryParentAPIView.as_view(), name='children of parent id'),
    url('^category(?:/(?P<id>.+))?/$', views.CategoryAPIView.as_view(), name='category api'),

    # Order
    url(r'^order/$', views.OrderAPIView.as_view(), name='order api get by tracking code'),
    path('send-method/', views.SendMethodAPIView.as_view(), name="send method api"),

    # Zibal Payment
    path('payment/request/zibal/', views.ZibalTransactionRequestAPIView.as_view(), name="payment request api"),
    url(r'^payment/callback/$', views.ZibalPaymentCallbackAPIView.as_view(), name="payment callback api"),

    # Offline Payment
    path('payment/request/offline/', views.OfflineTransactionRequestAPIView.as_view(), name="payment request api"),

    # Payment API
    url(r'^payment/$', views.PaymentAPIView.as_view(), name='payments api'),

]