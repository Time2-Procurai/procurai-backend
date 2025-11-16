from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.evaluation.models import Evaluation, EvaluationPhoto
from apps.evaluation.serializers.evaluation_serializer import EvaluationSerializer
from apps.products.models import Product
from apps.user.models import LojistaProfile
from rest_framework.parsers import MultiPartParser, FormParser

class ProductEvaluationView(generics.ListCreateAPIView):
    """
    Endpoint da API para avaliações de produtos.
    - GET: lista todas as avaliações de um produto específico
    - POST: cria uma nova avaliação para o produto
    """

    serializer_class = EvaluationSerializer
    # Mudar para IsAuthenticated para autenticação
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] 
    parser_classes = (MultiPartParser, FormParser)
    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return Evaluation.objects.filter(product__id=product_id).order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        # Juntando os dados do produto ao request data
        data = request.data.copy()
        data['product'] = product.id

        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Avaliação criada com sucesso.", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
    
class StoreEvaluationView(generics.ListCreateAPIView):
    # ... (queryset, serializer_class)
    
    # --- CORREÇÕES ---
    # 1. Somente usuários logados podem postar
    serializer_class = EvaluationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # 2. Essencial para aceitar FormData (fotos)
    parser_classes = (MultiPartParser, FormParser) 

    def get_queryset(self):
        # ... (seu queryset otimizado)
        store_id = self.kwargs.get('store_id')
        return Evaluation.objects.filter(store__id=store_id)\
                             .prefetch_related('photos', 'user')\
                             .order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        store_id = self.kwargs.get('store_id')
        store = get_object_or_404(LojistaProfile, id=store_id)

        data = request.data.copy()
        data['store'] = store.id # Envia o ID para o serializer

        # 3. Passa o 'request' para o 'context'
        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Avaliação criada com sucesso.", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )