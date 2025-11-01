"""
URL configuration for procurai_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.user.views import MyTokenObtainPairView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('apps.user.urls')),
    path('api/products/', include('apps.products.urls')),
    # Rota para Login (Obter token)
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Rota para Refresh (Atualizar token)
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]