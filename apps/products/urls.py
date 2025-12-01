from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductViewSet.as_view(), name='product-list-create'),
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