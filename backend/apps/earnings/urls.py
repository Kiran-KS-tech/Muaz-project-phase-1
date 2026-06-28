from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EarningUploadViewSet

router = DefaultRouter()
router.register(r'', EarningUploadViewSet, basename='earning')

urlpatterns = [
    path('', include(router.urls)),
]
