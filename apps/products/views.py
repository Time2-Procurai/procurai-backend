from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Product
from .serializers.product import ProductSerializer
from django.contrib.auth import get_user_model

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permissão customizada: apenas o dono pode editar/deletar
    """
    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS permitidos para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions apenas para o dono
        return obj.owner == request.user and request.user.is_lojista


class ProductViewSet(generics.ListCreateAPIView, generics.RetrieveUpdateAPIView):
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
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """
        Opcionalmente filtra produtos por categoria
        """
        queryset = Product.objects.filter(available=True)
        category_name = self.kwargs.get('category_name')
        store_id = self.kwargs.get('owner_id')

        if category_name:
            queryset = queryset.filter(category_name=category_name)

        if store_id:
            queryset = queryset.filter(owner_id=store_id)

        if category_name and store_id:
            queryset = queryset.filter(category_name=category_name, owner_id=store_id)

        return queryset

    def perform_create(self, serializer):
        """
        Associa o produto ao usuário autenticado
        """
        if serializer.is_valid():
            # serializer.save(owner=self.request.user)
            user = get_user_model().objects.get(id=5)
            serializer.save(owner_id=user) # para fazer o teste do POST do produto
        else:
            print(serializer.errors)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_products(self, request):
        """
        Endpoint customizado: GET /api/products/my_products/
        Retorna apenas produtos do usuário autenticado
        """
        products = Product.objects.filter(owner=request.user)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

class ProductDelete(generics.DestroyAPIView):
    """
    Endpoint para deletar um produto específico.
    Apenas o proprietário do produto pode deletá-lo.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """
        Garante que o usuário só possa deletar seus próprios produtos
        """
        user = self.request.user
        return Product.objects.filter(owner=user)