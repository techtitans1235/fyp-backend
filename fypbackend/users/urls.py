from django.urls import path
from .views import RegisterAPIView, LoginAPIView, UserAPIView , UserDetailAPIView,CreatePaymentAPIView , RefreshTokenAPIView , LogoutAPIView

urlpatterns = [
    path('register', RegisterAPIView.as_view(), name='register'),
    path('login', LoginAPIView.as_view(), name='login'),
    path('user', UserAPIView.as_view(), name='user-detail'), 
    path('logout', LogoutAPIView.as_view(), name='logout'),
 
    path('create-payment', CreatePaymentAPIView.as_view(), name='create-payment'),
    path('refersh-token', RefreshTokenAPIView.as_view(), name='refersh-token'),


]

