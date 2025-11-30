from django.shortcuts import render
from rest_framework import generics, permissions, status, views, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from apps.community.serializers.community_serializer import (
    CommunitySerializer,
    CommunityDetailSerializer,
    CommunityFollowSerializer,
    CommunityFollowerSerializer,
    CommunityFeedSerializer
)
from rest_framework.exceptions import PermissionDenied
from .serializers.community_serializer import PublicacaoSerializer
from apps.community.models import Community, Publicacao
from apps.user.models import User, LojistaProfile
from apps.community.models import Community, Publicacao, Curtida, Comentario
from .serializers.comment_like_serializer import CurtidaSerializer, ComentarioSerializer



class PublicacaoDetailView(generics.RetrieveAPIView):
    """
    Retorna os detalhes de uma publicação específica.
    GET /api/community/publicacoes/<int:pk>/
    """
    queryset = Publicacao.objects.all()
    serializer_class = PublicacaoSerializer
    permission_classes = [permissions.AllowAny]

class CommunityDetailView(generics.RetrieveAPIView):
    """
    Retorna os detalhes da comunidade. Se não existir, CRIA automaticamente.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = CommunityDetailSerializer

    def get_object(self):
        # O 'lojista_id' na URL é o ID do Usuário (User ID)
        user_id = self.kwargs.get("lojista_id")
        
        # Busca o perfil pelo ID do usuário
        lojista = get_object_or_404(LojistaProfile, user__id=user_id)
        
        # AUTO-REPAIR: Se a comunidade não existir, cria agora.
        community, created = Community.objects.get_or_create(
            lojista=lojista,
            defaults={
                'nome': f"Comunidade {lojista.company_name}",
                'descricao': f"Bem-vindo à comunidade oficial da {lojista.company_name}!"
            }
        )
        return community


class AllPublicacoesListView(generics.ListAPIView):
    """
    Endpoint para listar TODAS as publicações do sistema (Feed Global).
    GET /api/community/publicacoes/
    """
    # Busca todos os objetos e ordena do mais recente para o mais antigo
    queryset = Publicacao.objects.all().order_by('-data_publicacao')
    serializer_class = PublicacaoSerializer
    permission_classes = [permissions.AllowAny] # Aberto para todos verem
    
    # Configuração opcional de busca
    filter_backends = [filters.SearchFilter]
    search_fields = ['titulo', 'descricao', 'autor__full_name', 'comunidade__nome']    
# Seguir uma comunidade
class FollowCommunityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, community_id):
        community = get_object_or_404(Community, id=community_id)

        if request.user in community.seguidores.all():
            return Response(
                {"message": "Você já está seguindo esta comunidade.", "seguindo": True},
                status=status.HTTP_200_OK,
            )
      
        community.seguidores.add(request.user)
        community.save()

        return Response(
            {"message": "Você está agora seguindo esta comunidade.", "seguindo": True},
            status=status.HTTP_200_OK
        )
   
class UnfollowCommunityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, community_id):
        community = get_object_or_404(Community, id=community_id)

        if request.user not in community.seguidores.all():
            return Response(
                {"message": "Você não está seguindo esta comunidade.", "seguindo": False},
                status=status.HTTP_200_OK,
            )
      
        community.seguidores.remove(request.user)
        community.save()

        return Response(
            {"message": "Você deixou de seguir esta comunidade.", "seguindo": False},
            status=status.HTTP_200_OK
        )
    
class CommunityFollowersListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CommunityFollowerSerializer

    def get_queryset(self):
        community_id = self.kwargs.get("community_id")
        community = get_object_or_404(Community, id=community_id)
        return community.seguidores.all()
    
class SuggestedCommunitiesView(generics.ListAPIView):
    """
    Por enquanto apenas ordena por criação recente.
    Depois podemos melhorar com base em recomendação real (bota uma IA
    para André se apaixoanr).
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = CommunitySerializer

    def get_queryset(self):
        return Community.objects.all().order_by('-criada_em')[:20]
    
class IsFollowingCommunityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, community_id):
        community = get_object_or_404(Community, id=community_id)
        is_following = community.seguidores.filter(id=request.user.id).exists()

        return Response(
            {"seguindo": is_following},
            status=status.HTTP_200_OK
        )

class PublicacaoCreateView(generics.CreateAPIView):
    serializer_class = PublicacaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser) # Permite upload de imagens

    def perform_create(self, serializer):
        # Apenas lojistas podem criar publicação
        if not self.request.user.is_lojista:
            raise PermissionDenied("Apenas lojistas podem criar publicações.")

        # Obtém o perfil do lojista
        lojista_profile = get_object_or_404(LojistaProfile, user=self.request.user)

        # AUTO-REPAIR: Garante que a comunidade existe antes de postar
        comunidade, created = Community.objects.get_or_create(
            lojista=lojista_profile,
            defaults={
                'nome': f"Comunidade {lojista_profile.company_name}",
                'descricao': f"Bem-vindo à comunidade oficial da {lojista_profile.company_name}!"
            }
        )

        # Salva a publicação vinculada ao autor e à comunidade
        serializer.save(
            autor=self.request.user,
            comunidade=comunidade
        )


class PublicacaoListView(generics.ListAPIView):
    serializer_class = PublicacaoSerializer
    permission_classes = [permissions.AllowAny]  # Agora é público

    def get_queryset(self):
        comunidade_id = self.kwargs.get('comunidade_id')
        comunidade = get_object_or_404(Community, id=comunidade_id)
        return comunidade.publicacoes.all()

class CurtirPublicacaoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, publicacao_id):
        publicacao = get_object_or_404(Publicacao, id=publicacao_id)

        # verifica se já curtiu
        if Curtida.objects.filter(publicacao=publicacao, usuario=request.user).exists():
            return Response(
                {"message": "Você já curtiu esta publicação."},
                status=status.HTTP_200_OK
            )
        
        Curtida.objects.create(publicacao=publicacao, usuario=request.user)

        return Response(
            {"message": "Publicação curtida com sucesso."},
            status=status.HTTP_201_CREATED
        )

class DescurtirPublicacaoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, publicacao_id):
        publicacao = get_object_or_404(Publicacao, id=publicacao_id)

        curtida = Curtida.objects.filter(publicacao=publicacao, usuario=request.user).first()

        if not curtida:
            return Response(
                {"message": "Você não curtiu esta publicação."},
                status=status.HTTP_200_OK
            )
        
        curtida.delete()

        return Response(
            {"message": "Curtida removida."},
            status=status.HTTP_200_OK
        )

class ComentarPublicacaoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, publicacao_id):
        publicacao = get_object_or_404(Publicacao, id=publicacao_id)

        texto = request.data.get("texto")
        if not texto:
            return Response(
                {"error": "Texto do comentário é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST
            )

        comentario = Comentario.objects.create(
            publicacao=publicacao,
            autor=request.user,
            texto=texto
        )

        return Response(
            ComentarioSerializer(comentario).data,
            status=status.HTTP_201_CREATED
        )

class ListarComentariosView(generics.ListAPIView):
    serializer_class = ComentarioSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        publicacao_id = self.kwargs.get("publicacao_id")
        publicacao = get_object_or_404(Publicacao, id=publicacao_id)
        return publicacao.comentarios.all()


class UserFollowingListView(generics.ListAPIView):
    """
    GET /api/community/following/
    Retorna as comunidades que o usuário logado segue.
    """
    serializer_class = CommunityFeedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filtra comunidades onde o usuário atual está na lista de seguidores
        return Community.objects.filter(seguidores=self.request.user)


class FollowToggleView(views.APIView):
    """
    POST /api/community/<int:target_id>/follow/
    Alterna (Seguir/Desseguir) uma comunidade.
    Recebe o ID do LOJISTA (User ID), encontra a comunidade dele e segue.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, target_id):
        try:
            # 1. Encontra o perfil do lojista pelo ID do Usuário
            lojista_profile = LojistaProfile.objects.get(user__id=target_id)
            # 2. Encontra a comunidade desse lojista
            community = Community.objects.get(lojista=lojista_profile)
        except (LojistaProfile.DoesNotExist, Community.DoesNotExist):
            return Response(
                {"error": "Este lojista não possui uma comunidade ativa."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        user = request.user

        # Lógica de Toggle (Seguir/Desseguir)
        if user in community.seguidores.all():
            community.seguidores.remove(user)
            action = "unfollowed"
            msg = f"Você deixou de seguir a comunidade {community.nome}."
        else:
            community.seguidores.add(user)
            action = "followed"
            msg = f"Você agora segue a comunidade {community.nome}!"

        return Response({"status": action, "message": msg}, status=status.HTTP_200_OK)