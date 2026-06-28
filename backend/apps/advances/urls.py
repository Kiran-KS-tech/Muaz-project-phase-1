from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdvanceRequestViewSet

router = DefaultRouter()
router.register(r'', AdvanceRequestViewSet, basename='advance')

urlpatterns = [
    path('', include(router.urls)),
]
