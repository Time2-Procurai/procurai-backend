from django.urls import path
from .views import PublicacaoCreateView, PublicacaoListView

urlpatterns = [
    path('publicacoes/<int:comunidade_id>/'
         , PublicacaoCreateView.as_view(), name='publicacao-create'),

    path('publicacoes/<int:comunidade_id>/listar/'
         , PublicacaoListView.as_view(), name='publicacao-list'),
]