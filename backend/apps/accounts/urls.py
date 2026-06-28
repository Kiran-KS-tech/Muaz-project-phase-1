from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, OTPSendView, OTPVerifyView, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('otp/send/', OTPSendView.as_view(), name='otp_send'),
    path('otp/verify/', OTPVerifyView.as_view(), name='otp_verify'),
    path('', include(router.urls)),
]
