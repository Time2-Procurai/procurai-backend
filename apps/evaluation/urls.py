from django.urls import path
from . import views

urlpatterns = [
    path(
        'products/<int:product_id>/',
        views.ProductEvaluationView.as_view(),
        name='product-evaluations'
    ),
    path(
        'stores/<int:store_id>/',
        views.StoreEvaluationView.as_view(),
        name='store-evaluations'
    ),
]