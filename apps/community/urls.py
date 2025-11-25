from django.urls import path
from .views import (
    CommunityDetailView,
    FollowCommunityView,
    UnfollowCommunityView,
    CommunityFollowersListView,
    SuggestedCommunitiesView,
    IsFollowingCommunityView,
    CurtirPublicacaoView,
    DescurtirPublicacaoView,
    ComentarPublicacaoView,
    ListarComentariosView
)
from apps.community.views import PublicacaoCreateView, PublicacaoListView


app_name = 'community'

urlpatterns = [

    # Detalhes da comunidade
    path('lojista/<int:lojista_id>/', CommunityDetailView.as_view(), name='community-detail'),

    # Seguir / Desseguir
    path('<int:community_id>/follow/', FollowCommunityView.as_view(), name='community-follow'),
    path('<int:community_id>/unfollow/', UnfollowCommunityView.as_view(), name='community-unfollow'),

    # Lista de seguidores
    path('<int:community_id>/seguidores/', CommunityFollowersListView.as_view(), name='community-followers'),

    # Comunidades sugeridas
    path('sugeridas/', SuggestedCommunitiesView.as_view(), name='community-suggested'),

    # Verificar se o usuário está seguindo a comunidade
    path('<int:community_id>/esta-seguindo/', IsFollowingCommunityView.as_view(), name='community-is-following'),

    # Publicações na comunidade
    path('publicacoes/criar/', PublicacaoCreateView.as_view(), name='publicacao-create'),

    # Listar publicações na comunidade
    path('publicacoes/<int:comunidade_id>/listar/', PublicacaoListView.as_view(), name='publicacao-list'),

    # Curtir / Descurtir
    path('publicacoes/<int:publicacao_id>/curtir/', CurtirPublicacaoView.as_view(), name='publicacao-curtir'),
    path('publicacoes/<int:publicacao_id>/descurtir/', DescurtirPublicacaoView.as_view(), name='publicacao-descurtir'),

    # Comentários
    path('publicacoes/<int:publicacao_id>/comentar/', ComentarPublicacaoView.as_view(), name='publicacao-comentar'),
    path('publicacoes/<int:publicacao_id>/comentarios/', ListarComentariosView.as_view(), name='publicacao-comentarios'),

]