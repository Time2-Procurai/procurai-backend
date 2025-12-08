from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import ClienteCommunity
from .serializers.serializers import ClienteCommunitySerializer

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permite leitura para todos, mas edição/deleção apenas para o criador.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.criador == request.user

class ClienteCommunityViewSet(viewsets.ModelViewSet):
    queryset = ClienteCommunity.objects.all()
    serializer_class = ClienteCommunitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    # Configuração de Filtros (Busca por nome e Categoria)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria'] # Permite: /api/comunidades/?categoria=esportes
    search_fields = ['nome', 'descricao']
    ordering_fields = ['criada_em', 'nome']

    def perform_create(self, serializer):
        # Define automaticamente o usuário logado como criador
        serializer.save(criador=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def seguir(self, request, pk=None):
        comunidade = self.get_object()
        user = request.user
        
        if comunidade.seguidores.filter(id=user.id).exists():
            comunidade.seguidores.remove(user)
            # Retorna o total atualizado
            return Response(
                {'status': 'deixou de seguir', 'seguindo': False, 'total': comunidade.seguidores.count()}, 
                status=status.HTTP_200_OK
            )
        else:
            comunidade.seguidores.add(user)
            # Retorna o total atualizado
            return Response(
                {'status': 'seguindo', 'seguindo': True, 'total': comunidade.seguidores.count()},
                status=status.HTTP_200_OK
            )