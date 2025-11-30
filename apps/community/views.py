from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

# Imports do Model
from apps.community.models import (
    Community, Publicacao, Curtida, Comentario, 
    Enquete, OpcaoEnquete, VotoEnquete
)
from apps.user.models import LojistaProfile

# Imports de Serializers
from apps.community.serializers.community_serializer import (
    CommunitySerializer,
    CommunityDetailSerializer,
    CommunityFollowerSerializer,
    PublicacaoSerializer,
)
from apps.community.serializers.comment_like_serializer import (
    CurtidaSerializer, 
    ComentarioSerializer
)
from apps.community.serializers.enquete_serializer import (
    EnqueteSerializer, 
    CriarEnqueteSerializer, 
    VotoEnqueteSerializer
)

class CommunityDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CommunityDetailSerializer

    def get_object(self):
        lojista_id = self.kwargs.get("lojista_id")
        lojista = get_object_or_404(LojistaProfile, id=lojista_id)
        return lojista.community

class FollowCommunityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, community_id):
        community = get_object_or_404(Community, id=community_id)
        if request.user in community.seguidores.all():
            return Response({"message": "Você já segue esta comunidade.", "seguindo": True}, status=status.HTTP_200_OK)
        
        community.seguidores.add(request.user)
        return Response({"message": "Agora você segue esta comunidade.", "seguindo": True}, status=status.HTTP_200_OK)

class UnfollowCommunityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, community_id):
        community = get_object_or_404(Community, id=community_id)
        if request.user not in community.seguidores.all():
            return Response({"message": "Você não segue esta comunidade.", "seguindo": False}, status=status.HTTP_200_OK)
        
        community.seguidores.remove(request.user)
        return Response({"message": "Deixou de seguir a comunidade.", "seguindo": False}, status=status.HTTP_200_OK)

class CommunityFollowersListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CommunityFollowerSerializer

    def get_queryset(self):
        community = get_object_or_404(Community, id=self.kwargs.get("community_id"))
        return community.seguidores.all()

class SuggestedCommunitiesView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CommunitySerializer

    def get_queryset(self):
        return Community.objects.all().order_by('-criada_em')[:20]

class IsFollowingCommunityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, community_id):
        community = get_object_or_404(Community, id=community_id)
        is_following = community.seguidores.filter(id=request.user.id).exists()
        return Response({"seguindo": is_following}, status=status.HTTP_200_OK)

class PublicacaoCreateView(generics.CreateAPIView):
    serializer_class = PublicacaoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if not self.request.user.is_lojista:
            raise PermissionDenied("Apenas lojistas podem criar publicações.")
        
        lojista_profile = get_object_or_404(LojistaProfile, user=self.request.user)
        serializer.save(autor=self.request.user, comunidade=lojista_profile.community)

class PublicacaoListView(generics.ListAPIView):
    serializer_class = PublicacaoSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        community = get_object_or_404(Community, id=self.kwargs.get('comunidade_id'))
        return community.publicacoes.all()

class CurtirPublicacaoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, publicacao_id):
        publicacao = get_object_or_404(Publicacao, id=publicacao_id)
        if Curtida.objects.filter(publicacao=publicacao, usuario=request.user).exists():
            return Response({"message": "Já curtido."}, status=status.HTTP_200_OK)
        
        Curtida.objects.create(publicacao=publicacao, usuario=request.user)
        return Response({"message": "Curtido com sucesso."}, status=status.HTTP_201_CREATED)

class DescurtirPublicacaoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, publicacao_id):
        publicacao = get_object_or_404(Publicacao, id=publicacao_id)
        Curtida.objects.filter(publicacao=publicacao, usuario=request.user).delete()
        return Response({"message": "Curtida removida."}, status=status.HTTP_200_OK)

class ComentarPublicacaoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, publicacao_id):
        publicacao = get_object_or_404(Publicacao, id=publicacao_id)
        texto = request.data.get("texto")
        if not texto:
            return Response({"error": "Texto obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        comentario = Comentario.objects.create(publicacao=publicacao, autor=request.user, texto=texto)
        return Response(ComentarioSerializer(comentario).data, status=status.HTTP_201_CREATED)

class ListarComentariosView(generics.ListAPIView):
    serializer_class = ComentarioSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        publicacao = get_object_or_404(Publicacao, id=self.kwargs.get("publicacao_id"))
        return publicacao.comentarios.all()

class EnqueteViewSet(viewsets.ModelViewSet):
    """
    Gerencia Listagem, Criação, Detalhes e Votação de Enquetes.
    Substitui: CriarEnqueteView, ListarEnquetesView, Detalhar, Votar, Resultado.
    """
    # Traz opções junto para evitar query extra 
    queryset = Enquete.objects.all().prefetch_related('opcoes').order_by('-criada_em')
    
    # Permite filtrar por comunidade na URL: /api/enquetes/?comunidade=ID
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['comunidade'] 

    def get_permissions(self):
        """Define permissões dinamicamente baseadas na ação."""
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            # Apenas autenticados (e lojistas, verificado no perform_create)
            return [permissions.IsAuthenticated()]
        elif self.action == 'votar':
            return [permissions.IsAuthenticated()]
        else:
            # Listar e Detalhar é público
            return [permissions.AllowAny()]

    def get_serializer_class(self):
        """Troca o serializer dependendo da operação."""
        if self.action == 'create':
            return CriarEnqueteSerializer
        if self.action == 'votar':
            return VotoEnqueteSerializer
        # Para list e retrieve, usa o completo (com contagem de votos)
        return EnqueteSerializer

    def perform_create(self, serializer):
        """
        Injeta automaticamente o autor e a comunidade ao criar.
        """
        user = self.request.user
        if not user.is_lojista:
            raise PermissionDenied("Apenas lojistas podem criar enquetes.")
        
        lojista = get_object_or_404(LojistaProfile, user=user)
        serializer.save(autor=user, comunidade=lojista.community)

    def create(self, request, *args, **kwargs):
        """
        Sobrescrita opcional para retornar o JSON completo (com ID e Total Votos)
        após a criação, em vez de apenas os dados de entrada.
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        enquete = serializer.save() # Chama perform_create internamente
        
        # Serializa a resposta com o serializer de leitura (mais bonito para o front)
        read_serializer = EnqueteSerializer(enquete)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def votar(self, request, pk=None):
        """
        Endpoint: POST /api/enquetes/{id}/votar/
        Body: { "opcao_id": 5 }
        """
        serializer = VotoEnqueteSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {"message": "Voto computado com sucesso!"}, 
            status=status.HTTP_201_CREATED
        )