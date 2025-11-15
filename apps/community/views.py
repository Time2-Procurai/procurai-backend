from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.community.models import Community
from apps.community.serializers.community_serializer import (
    CommunitySerializer,
    CommunityDetailSerializer,
    CommunityFollowSerializer,
    CommunityFollowerSerializer,
)

from apps.user.models import User, LojistaProfile

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