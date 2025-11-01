from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductViewSet.as_view(), name='product-list-create'),
    path("delete/<int:pk>/", views.ProductDelete.as_view(), name="product-delete"),
    path("<int:pk>/", views.ProductViewSet.as_view(), name="product-detail"),
    path("<str:category_name>/", views.ProductViewSet.as_view(), name="product-by-category"),
    path("store/<int:owner_id>/", views.ProductViewSet.as_view(), name="products-by-store"),
    path("<int:owner_id>/<str:category_name>", views.ProductViewSet.as_view(), name="category-by-store"),
]