from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Product, Category
from .serializers.product import ProductSerializer, CategorySerializer

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permissão customizada: apenas o dono pode editar/deletar
    """
    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS permitidos para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions apenas para o dono
        return obj.owner == request.user


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD completo de produtos
    
    list: GET /api/products/ - Lista todos produtos disponíveis
    retrieve: GET /api/products/{id}/ - Detalhes de um produto
    create: POST /api/products/ - Criar produto (requer autenticação)
    update: PUT /api/products/{id}/ - Atualizar produto (apenas dono)
    partial_update: PATCH /api/products/{id}/ - Atualizar parcialmente (apenas dono)
    destroy: DELETE /api/products/{id}/ - Deletar produto (apenas dono)
    """
    queryset = Product.objects.filter(available=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        """
        Opcionalmente filtra produtos por categoria
        """
        queryset = Product.objects.filter(available=True)
        category_slug = self.request.query_params.get('category', None)
        
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Associa o produto ao usuário autenticado
        """
        serializer.save(owner=self.request.user)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_products(self, request):
        """
        Endpoint customizado: GET /api/products/my_products/
        Retorna apenas produtos do usuário autenticado
        """
        products = Product.objects.filter(owner=request.user)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet apenas leitura para categorias
    
    list: GET /api/categories/ - Lista todas categorias
    retrieve: GET /api/categories/{id}/ - Detalhes de uma categoria
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'  # Permite buscar por slug: /api/categories/eletronicos/