from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Product
from .serializers.product import ProductSerializer
from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser

"Inserindo permissões para lojistas autenticados"
class IsLojistaOrReadOnly(permissions.BasePermission):
    """
    Permite leitura (GET, HEAD, OPTIONS) para qualquer um.
    Permite escrita (POST, PUT, PATCH) apenas se o usuário
    estiver autenticado E for um lojista.
    """

    def has_permission(self, request, view):
        # Permite métodos seguros (GET, HEAD, OPTIONS) para todos
        if request.method in permissions.SAFE_METHODS:
            return True

        # Se não for um método seguro, verifica se o usuário
        # está autenticado e é um Lojista.
        # (Assumindo que seu User model tem o campo 'is_lojista')
        return request.user.is_authenticated and request.user.is_lojista

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permissão customizada: apenas o dono pode editar/deletar
    """
    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS permitidos para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions apenas para o dono
        return obj.owner_id == request.user and request.user.is_lojista


class ProductViewSet(generics.ListCreateAPIView, generics.RetrieveUpdateAPIView):
    """
    ViewSet para CRUD completo de produtos
    """
    queryset = Product.objects.filter(available=True)
    serializer_class = ProductSerializer
    permission_classes = [IsLojistaOrReadOnly, IsOwnerOrReadOnly]
    parser_classes = (MultiPartParser, FormParser) # (Garante que os parsers estão aqui)

    # --- AJUSTE AQUI ---
    # Adicione este método 'get'
    def get(self, request, *args, **kwargs):
        """
        Verifica se um 'pk' (ID do produto) foi passado na URL.
        Se sim, chama a lógica de 'retrieve' (detalhe).
        Se não, chama a lógica de 'list' (lista).
        """
        if 'pk' in kwargs:
            return self.retrieve(request, *args, **kwargs)
        
        return self.list(request, *args, **kwargs)
    # --- FIM DO AJUSTE ---

    def get_queryset(self):
        """
        Opcionalmente filtra produtos por categoria ou loja.
        (Este método agora funcionará corretamente para a lista)
        """
        queryset = Product.objects.filter(available=True)
        category_name = self.kwargs.get('category_name')
        store_id = self.kwargs.get('owner_id')

        # Se a URL for /products/store/ID/, filtra pela loja
        if store_id:
            queryset = queryset.filter(owner_id=store_id)
        # Se for /products/categoria/, filtra pela categoria
        elif category_name:
            queryset = queryset.filter(category_name=category_name)
        # Se for /products/ (sem ID ou categoria), não filtra mais
        # (A lógica de filtrar por usuário logado não deve estar aqui,
        # a menos que seja para a rota 'my_products')
            
        return queryset

    def perform_create(self, serializer):
        """
        Associa o produto ao usuário autenticado (request.user)
        """
        # (Simplificado para ser mais robusto)
        serializer.save(owner_id=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_products(self, request):
        """
        Endpoint customizado: GET /api/products/my_products/
        Retorna apenas produtos do usuário autenticado
        """
        products = Product.objects.filter(owner_id=request.user)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

class ProductDelete(generics.DestroyAPIView):
    """
    Endpoint para deletar um produto específico.
    Apenas o proprietário do produto pode deletá-lo.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    def get_queryset(self):
        """
        Garante que o usuário só possa deletar seus próprios produtos
        """
        user = self.request.user
        return Product.objects.filter(owner_id=user)
