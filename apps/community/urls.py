from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommunityDetailView,
    CurtirPublicacaoView,
    DescurtirPublicacaoView,
    ComentarPublicacaoView,
    ListarComentariosView,
    EnqueteViewSet,
    FollowToggleView,
    PublicacaoDetailView,
)
app_name = 'community'
router = DefaultRouter()
router.register(r'enquetes', EnqueteViewSet, basename='enquete')

urlpatterns = [
    
    path('', include(router.urls)),
    # Detalhes da comunidade
    path('lojista/<int:lojista_id>/', views.CommunityDetailView.as_view(), name='community-detail'),

    # --- Publicações (Certifique-se que esta rota existe) ---
    path('publicacoes/criar/', views.PublicacaoCreateView.as_view(), name='publicacao-create'),
    path('publicacoes/<int:comunidade_id>/listar/', views.PublicacaoListView.as_view(), name='publicacao-list'),
    path('publicacoes/', views.AllPublicacoesListView.as_view(), name='publicacao-list-all'),
    # Ações de Publicação
    path('publicacoes/<int:publicacao_id>/curtir/', views.CurtirPublicacaoView.as_view(), name='publicacao-curtir'),
    path('publicacoes/<int:publicacao_id>/descurtir/', views.DescurtirPublicacaoView.as_view(), name='publicacao-descurtir'),
    path('publicacoes/<int:publicacao_id>/comentar/', views.ComentarPublicacaoView.as_view(), name='publicacao-comentar'),
    path('publicacoes/<int:publicacao_id>/comentarios/', views.ListarComentariosView.as_view(), name='publicacao-comentarios'),
     path('publicacoes/<int:pk>/', views.PublicacaoDetailView.as_view(), name='publicacao-detail'),
    # Seguir / Desseguir e Seguidores
    path('<int:target_id>/follow/', views.FollowToggleView.as_view(), name='community-follow'),
    path('<int:target_id>/unfollow/', views.FollowToggleView.as_view(), name='community-unfollow'),
    path('<int:community_id>/seguidores/', views.CommunityFollowersListView.as_view(), name='community-followers'),
    path('<int:community_id>/esta-seguindo/', views.IsFollowingCommunityView.as_view(), name='community-is-following'),

    # Outras rotas
    path('sugeridas/', views.SuggestedCommunitiesView.as_view(), name='community-suggested'),
    path('following/', views.UserFollowingListView.as_view(), name='community-following'),
    path('publicacoes/<int:pk>/', PublicacaoDetailView.as_view(), name='publicacao-detail'),
    # --- ROTAS PARA ENQUETES ---
    # Listar e Criar (POST envia {pergunta, opcoes: []})
    path('enquetes/', views.EnqueteViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='enquete-list-create'),

    # Votar (POST envia {opcao_id: 1})
    path('enquetes/<int:pk>/votar/', views.EnqueteViewSet.as_view({
        'post': 'votar'
    }), name='enquete-votar'),
    
    # Detalhes/Deletar
    path('enquetes/<int:pk>/', views.EnqueteViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy'
    }), name='enquete-detail'),
]