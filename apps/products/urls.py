from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import ProductListCreateView, ProductDetailView, MyProductsView


urlpatterns = [
    path('', ProductListCreateView.as_view(), name='product-list-create'),

    # Rota para "Meus Produtos" (Deve vir ANTES do ID para não confundir)
    path('my_products/', MyProductsView.as_view(), name='my-products'),

    # Rota para Detalhes (GET), Atualizar (PUT) e Deletar (DELETE)
    # É AQUI QUE O CONTADOR FUNCIONA (ao acessar essa URL)
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path("search/", views.ProductListView.as_view(), name="product-search"),
    path("delete/<int:pk>/", views.ProductDelete.as_view(), name="product-delete"),
    path("<int:pk>/", views.ProductViewSet.as_view(), name="product-detail"), # pode ser removida
    path("<str:category_name>/", views.ProductViewSet.as_view(), name="product-by-category"), # pode ser removida
    path("store/<int:owner_id>/", views.ProductViewSet.as_view(), name="products-by-store"), # pode ser removida
    path("<int:owner_id>/<str:category_name>", views.ProductViewSet.as_view(), name="category-by-store"), # pode ser removida
    
    # Rota para listar (deve vir antes de rotas com ID dinâmico para evitar conflito)
    path('favorites/', views.UserFavoritesListView.as_view(), name='user-favorites-list'),
    
    # Rota para favoritar/desfavoritar (Toggle)
    path('favorite/<int:product_id>/', views.ToggleFavoriteView.as_view(), name='toggle-favorite'),
    path('favorites/all/', views.AllFavoritesListView.as_view(), name='all-favorites-list'), # Todos os Favoritos (Admin)
    path('favorites/user/<int:user_id>/', views.FavoritesByUserIdView.as_view(), name='favorites-by-user-id'),
]