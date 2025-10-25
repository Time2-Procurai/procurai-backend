from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'products'

# Router do DRF gera automaticamente as URLs
router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'categories', views.CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]

# URLs geradas automaticamente:
# GET    /api/products/              - Lista produtos
# POST   /api/products/              - Criar produto
# GET    /api/products/{id}/         - Detalhe produto
# PUT    /api/products/{id}/         - Atualizar produto
# PATCH  /api/products/{id}/         - Atualizar parcialmente
# DELETE /api/products/{id}/         - Deletar produto
# GET    /api/products/my_products/  - Produtos do usuário
# GET    /api/categories/            - Lista categorias
# GET    /api/categories/{slug}/     - Detalhe categoria