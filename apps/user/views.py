
from .models import ClienteProfile
from django.shortcuts import render,redirect,get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, status

from rest_framework.permissions import AllowAny,IsAuthenticated

from django.shortcuts import get_object_or_404
from .models import User, LojistaProfile
from .serializers.profile import ClienteProfileSerializer
from .serializers.profile import Tela3LojistaEnderecoSerealizer
from .serializers.profile import Tela2LojistaSerializer
from .serializers.registration import Tela1UserCreationSerializer
from apps.user.serializers.deleteUser import UserBasicSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers.serializers import MyTokenObtainPairViewSerializer

class ClienteProfileRegistrationView(generics.CreateAPIView):
    """
    Endpoint da API para a Etapa 2 do cadastro de Cliente.
    Recebe um user_id na URL para saber a qual usuário associar o perfil.
    """
    queryset = ClienteProfile.objects.all()
    serializer_class = ClienteProfileSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Usuário com o ID fornecido não foi encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        if hasattr(user, 'cliente_profile'):
            return Response(
                {"error": "Este usuário já possui um perfil de cliente."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
    
        # Em vez de: cliente_profile = serializer.save()
        # Diga ao save() qual usuário ele deve associar:
        cliente_profile = serializer.save(user=user)
        
        return Response(
            {
                "message": "Cadastro de cliente finalizado com sucesso!",
                "user_id": cliente_profile.user.id,
                "profile_id": cliente_profile.id
            },
            status=status.HTTP_201_CREATED
        )


class DeletarContaView(generics.GenericAPIView):
    """
    Recebe uma requisição DELETE autenticada (via token/JWT)
    e deleta o usuário que fez a requisição (request.user).
    """
    
   
    permission_classes = [IsAuthenticated] 
    
   
    def perform_destroy(self, instance):
       
        instance.delete()

    def delete(self, request, *args, **kwargs):
        
        # 4. 'request.user' é o usuário identificado pelo token.
        # Esta é a "sessão" que você mencionou.
        user_to_delete = request.user 

        # (Opcional) Salva os dados do usuário para a resposta
        user_data = UserBasicSerializer(user_to_delete).data
        
        # 5. Deleta o usuário
        self.perform_destroy(user_to_delete)
        
        return Response(
            {"message": "Conta apagada com sucesso", "user": user_data},
            status=status.HTTP_200_OK
           
        )

class Tela1UserRegistrationView(generics.CreateAPIView):
    """
    Endpoint da API para a primeita etapa de cadastro de usuario.
    Vai receber os dados da primeira tela e criar o usuário base.
    """
    queryset = User.objects.all()

    # Conectar a view ao DTO da Tela 1
    serializer_class = Tela1UserCreationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # Passando os dados recebidos para o DTO
        serializer = self.get_serializer(data=request.data)

        # Executando validações do DTO
        serializer.is_valid(raise_exception=True)

        # Salvando o usuário
        user = serializer.save()

        return Response(
            {
                "message": "Etapa 1 concluída. Usuário base criado.",
                "user_id": user.id
            },
            status=status.HTTP_201_CREATED
        )

class Tela2LojistaProfileView(generics.CreateAPIView):
    """
    Endpoint da API para a segunda etapa de cadastro de usuário, agora um lojista.
    Cria o LojistaProfile e o associa a um User existente e criado na Etapa 1.
    """
    queryset = LojistaProfile.objects.all()
    serializer_class = Tela2LojistaSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)

        if not user.is_lojista:
            return Response({"error": "Este usuário não é lojista."}, status=status.HTTP_400_BAD_REQUEST)
        if hasattr(user, 'lojista_profile'):
            return Response({"error": "Este usuário já possui um perfil."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {"message": "Etapa 2 concluída. Perfil da empresa preenchido."}
        )

    def perform_create(self, serializer):
        serializer.save()

class Tela3LojistaEnderecoView(generics.UpdateAPIView):
    """
    Endpoint da API para a Etapa 3 do cadastro de Lojista.
    Atualiza (PATCH) um LojistaProfile existente com os dados de endereço.
    """
    queryset = LojistaProfile.objects.all()
    serializer_class = Tela3LojistaEnderecoSerealizer
    permission_classes = [AllowAny]

    lookup_field = 'user__id'
    lookup_url_kwarg = 'user_id'

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)

        if response.status_code == 200:
            return Response(
                {"message": "Cadastro finalizado com sucesso!"},
                status.HTTP_200_OK
            )

        return Response
    

    # ... (no final do arquivo, depois de Tela3LojistaEnderecoView)

class MyTokenObtainPairView(TokenObtainPairView):
    """
    Endpoint de Login.
    Recebe 'email' e 'password', retorna 'access' e 'refresh' tokens.
    O 'access' token conterá o 'role' (cliente/lojista).
    """
    serializer_class = MyTokenObtainPairViewSerializer