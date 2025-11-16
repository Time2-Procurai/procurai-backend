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
    (Esta view está correta, não precisa de mudanças)
    """
    serializer_class = EvaluationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] 
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return Evaluation.objects.filter(product__id=product_id).order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)

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
    """
    Endpoint da API para avaliações de lojas.
    (Corrigido para buscar pelo user_id)
    """
    serializer_class = EvaluationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser) 

    def get_queryset(self):
        # --- CORREÇÃO AQUI ---
        # O 'store_id' da URL é, na verdade, o ID do *usuário*
        user_id = self.kwargs.get('store_id')
        # Filtra as avaliações buscando pelo user_id do LojistaProfile
        return Evaluation.objects.filter(store__user_id=user_id)\
                                 .prefetch_related('photos', 'user')\
                                 .order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        # --- CORREÇÃO AQUI ---
        # 1. Pega o ID da URL (que é o ID do Usuário)
        user_id = self.kwargs.get('store_id')
        
        # 2. Busca o LojistaProfile usando o 'user_id' (a FK para User)
        store = get_object_or_404(LojistaProfile, user_id=user_id)

        # 3. Agora 'store.id' é o ID correto do LojistaProfile
        data = request.data.copy()
        data['store'] = store.id # Envia o ID do *Perfil* (ex: 5) para o serializer

        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Avaliação criada com sucesso.", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )