from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.community.serializers.community_serializer import (
    CommunitySerializer,
    CommunityDetailSerializer,
    CommunityFollowSerializer,
    CommunityFollowerSerializer,
)
from rest_framework.exceptions import PermissionDenied
from .serializers.community_serializer import PublicacaoSerializer
from apps.community.models import Community, Publicacao
from apps.user.models import User, LojistaProfile
from .permissions import IsAutorDaPublicacao



class CommunityDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CommunityDetailSerializer

    def get_object(self):
        lojista_id = self.kwargs.get("lojista_id")
        lojista = get_object_or_404(LojistaProfile, id=lojista_id)
        return lojista.community
    
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

    def perform_create(self, serializer):

        # Apenas lojistas podem criar publicação
        if not self.request.user.is_lojista:
            raise PermissionDenied("Apenas lojistas podem criar publicações.")

        # Obtém o perfil do lojista
        lojista_profile = get_object_or_404(LojistaProfile, user=self.request.user)

        # Obtém automaticamente a comunidade associada ao lojista
        comunidade = lojista_profile.community

        # Salva a publicação com autor e comunidade definidos automaticamente
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

class PublicacaoDeleteView(generics.DestroyAPIView):
    """
    Endpoint para deletar uma publicação específica.
    Apenas o autor da publicação pode deletá-la.
    """
    queryset = Publicacao.objects.all()
    serializer_class = PublicacaoSerializer
    permission_classes = [permissions.IsAuthenticated, IsAutorDaPublicacao]

