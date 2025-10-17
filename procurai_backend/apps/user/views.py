from .models import Cliente
from django.shortcuts import render,redirect,get_object_or_404
from rest_framework.decorators import api_view
from .forms import ClienteForm
from rest_framework.response import Response
from .serializers import ClienteSerializer

@api_view(['POST'])
def criar_cliente(request):
    serializer = ClienteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)      
           

@api_view(['GET'])
def retornar_clientes(request):
    clientes = Cliente.objects.all()
    serializer = ClienteSerializer(clientes, many=True)
    return Response(serializer.data)