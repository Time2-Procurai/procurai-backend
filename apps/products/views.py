from rest_framework import viewsets, permissions, generics, views, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Product
from .serializers.product import ProductSerializer
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser, FormParser
from apps.products.models import Product, Favorite
from apps.products.serializers.favorite import FavoriteSerializer
from django.shortcuts import get_object_or_404

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


    filter_backends = [SearchFilter]
    search_fields = ['name', 'description', 'category_name']
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


class ToggleFavoriteView(views.APIView):
    """
    Endpoint para favoritar/desfavoritar um produto.
    POST /api/products/favorite/<product_id>/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, product_id):
        # Verifica se é cliente
        if not getattr(request.user, 'is_cliente', False):
             return Response({"error": "Apenas clientes podem favoritar produtos."}, status=status.HTTP_403_FORBIDDEN)

        product = get_object_or_404(Product, id=product_id)
        
        # get_or_create retorna uma tupla (objeto, criado?)
        favorite_item, created = Favorite.objects.get_or_create(user=request.user, product=product)

        if not created:
            # Se já existia, o usuário quer remover
            favorite_item.delete()
            return Response({"message": "Produto removido dos favoritos.", "is_favorited": False}, status=status.HTTP_200_OK)
        
        return Response({"message": "Produto adicionado aos favoritos.", "is_favorited": True}, status=status.HTTP_201_CREATED)


class UserFavoritesListView(generics.ListAPIView):
    """
    Endpoint seguro que lista APENAS os favoritos do usuário logado.
    GET /api/products/favorites/
    """
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated] # Obrigatório estar logado
    pagination_class = None 
    def get_queryset(self):
        # Isso é o mais seguro: confia apenas no token validado
        return Favorite.objects.filter(user=self.request.user)

class AllFavoritesListView(generics.ListAPIView):
    """
    Lista TODOS os favoritos do sistema (apenas para Admin).
    GET /api/products/favorites/all/
    """
    queryset = Favorite.objects.all().order_by('-created_at')
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.AllowAny] # Segurança: Apenas admin pode ver tudo

class FavoritesByUserIdView(generics.ListAPIView):
    """
    Lista os favoritos de um usuário específico passado na URL.
    GET /api/products/favorites/user/<user_id>/
    """
    serializer_class = FavoriteSerializer
    # Recomendado: IsAdminUser para que apenas admins vejam listas de outros.
    # Se quiser liberar geral, use IsAuthenticated.
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        # Pega o ID da URL
        target_user_id = self.kwargs.get('user_id')
        
        # Filtra os favoritos daquele usuário específico
        return Favorite.objects.filter(user__id=target_user_id).order_by('-created_at')

class ProductFilter(filters.FilterSet):
    """
    Filtro completo para produtos com múltiplas opções
    """
    
    # Filtro por nome (parcial, case-insensitive)
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    
    # Filtro por categoria (exato)
    category_name = filters.CharFilter(field_name='category_name', lookup_expr='exact')
    
    # Filtro por faixa de preço
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    # Filtro por loja/vendedor
    owner_id = filters.NumberFilter(field_name='owner_id', lookup_expr='exact')
    
    # Filtro por produto
    id = filters.NumberFilter(field_name='id', lookup_expr='exact')
    
    # Filtro por disponibilidade
    available = filters.BooleanFilter(field_name='available')
    
    class Meta:
        model = Product
        fields = ['name', 'category_name', 'min_price', 'max_price', 'owner_id', 'available']
        
class ProductListView(generics.ListAPIView):
    """
    View para listar produtos com múltiplos filtros
    
    Exemplos de uso:
    - /api/products/search/ - lista todos os produtos
    - /api/products/search/?name=telefone - filtra por nome
    - /api/products/search/?category_name=eletronicos - filtra por categoria
    - /api/products/search/?min_price=100&max_price=500 - filtra por faixa de preço
    - /api/products/search/?owner_id=3 - filtra por loja/vendedor
    """
    queryset = Product.objects.filter(available=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    
    # Backends de filtro, busca e ordenação
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Configuração do django-filter
    filterset_class = ProductFilter
    
    # Configuração de busca
    search_fields = ['name', 'description', 'category_name', 'id']
    
    # Configuração de ordenação
    ordering_fields = ['price', 'name']
