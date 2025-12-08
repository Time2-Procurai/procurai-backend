from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteCommunityViewSet

router = DefaultRouter()
router.register(r'comunidades', ClienteCommunityViewSet, basename='cliente-community')

urlpatterns = [
    path('', include(router.urls)),
]