from django.urls import path
# Importamos as novas views baseadas em classes
from .views import ClienteCreateView, LojistaCreateView

app_name = 'user'

urlpatterns = [
    # Rota para o cadastro de cliente
    path('cadastro/cliente/', ClienteCreateView.as_view(), name='cadastro-cliente'),

    # Rota para o cadastro de lojista
    path('cadastro/lojista/', LojistaCreateView.as_view(), name='cadastro-lojista'),
]