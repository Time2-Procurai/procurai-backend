from rest_framework import generics
from .models import User
from .serializers import ClienteCreateSerializer, LojistaCreateSerializer

# Endpoint para CRIAR um novo Cliente
class ClienteCreateView(generics.CreateAPIView):
    queryset = User.objects.filter(is_cliente=True)
    serializer_class = ClienteCreateSerializer

# Endpoint para CRIAR um novo Lojista (já vamos deixar pronto)
class LojistaCreateView(generics.CreateAPIView):
    queryset = User.objects.filter(is_lojista=True)
    serializer_class = LojistaCreateSerializer