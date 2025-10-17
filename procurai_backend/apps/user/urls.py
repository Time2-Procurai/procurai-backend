from django.urls import path
from . import views

urlpatterns = [
    path('clientes/', views.retornar_clientes, name='retornar_clientes'),
    path('clientes/criar/', views.criar_cliente, name='criar_cliente'),
]
