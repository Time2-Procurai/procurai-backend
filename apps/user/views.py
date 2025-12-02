
from .models import ClienteProfile,User
from django.shortcuts import render,redirect,get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers.serializers import MyTokenObtainPairViewSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import User, LojistaProfile ,PasswordResetCode
from .serializers.profile import ClienteProfileSerializer,UserListSerializer
from .serializers.profile import Tela3LojistaEnderecoSerealizer
from .serializers.profile import Tela2LojistaSerializer
from .serializers.registration import Tela1UserCreationSerializer
from .serializers.deleteUser import UserBasicSerializer
from apps.user.serializers.deleteUser import UserBasicSerializer
from .serializers.profile import UserDataSerializer,ClienteProfileRegistrationSerializer,LojistaProfileDataSerializer,ClienteProfileDataSerializer
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .serializers.password import PasswordChangeSerializer, PasswordResetConfirmCodeSerializer,PasswordResetRequestSerializer, PasswordResetValidateCodeSerializer
from .serializers.serializers import UserDetailSerializer
from rest_framework.filters import SearchFilter

from django.contrib.auth import get_user_model



from rest_framework.permissions import AllowAny
from apps.community.models import Community
class ClienteProfileRegistrationView(generics.UpdateAPIView):
    """
    Endpoint da API para a Etapa 2 do cadastro de Cliente.
    Recebe um user_id na URL e ATUALIZA o User com 'full_name', 'cpf', etc.
    e CRIA o ClienteProfile associado (com a imagem).
    """
    # 1. Estamos atualizando um 'User', não criando um 'ClienteProfile'
    queryset = User.objects.all()
    
    # 2. Precisamos do serializer que lida com dados aninhados (User + Profile)
    serializer_class = ClienteProfileRegistrationSerializer
    
    # 3. ADICIONE ISTO: Permite que a view entenda uploads de arquivos (multipart/form-data)
    parser_classes = (MultiPartParser, FormParser)
    
    permission_classes = [AllowAny]
    
    # 4. Define como encontrar o usuário pela URL
    lookup_field = 'id'
    lookup_url_kwarg = 'user_id'

    def post(self, request, *args, **kwargs):
        """
        Sobrescreve o 'post' para que ele se comporte como um 'patch' (atualização parcial).
        O seu React está enviando um POST.
        """
        # 'partial_update' é a lógica exata que precisamos:
        # Pega o 'user' da URL, aplica os dados do 'request' (incluindo a foto)
        # e salva usando a lógica do nosso novo serializer.
        return self.partial_update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        # Chama o processo de atualização padrão
        response = super().partial_update(request, *args, **kwargs)
        
        # Retorna uma resposta de sucesso customizada
        return Response(
            {
                "message": "Cadastro de cliente finalizado com sucesso!",
                "user_data": response.data
            },
            status=status.HTTP_200_OK
        )
        
class MyTokenObtainPairView(TokenObtainPairView):
    """
    Endpoint de Login.
    Recebe 'email' e 'password', retorna 'access' e 'refresh' tokens.
    O 'access' token conterá o 'role' (cliente/lojista).
    """
    serializer_class = MyTokenObtainPairViewSerializer


class DeletarContaView(generics.GenericAPIView):
    """
    Recebe uma requisição DELETE autenticada (via token/JWT)
    e deleta o usuário que fez a requisição (request.user).
    """
    permission_classes = [IsAuthenticated] 
    
    def perform_destroy(self, instance):
        instance.delete()

    def delete(self, request, *args, **kwargs):
        #'request.user' é o usuário identificado pelo token
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
    Endpoint da API para a segunda etapa de cadastro de usuário (Lojista).
    Cria o LojistaProfile e AUTOMATICAMENTE cria uma Comunidade vinculada.
    """
    queryset = LojistaProfile.objects.all()
    serializer_class = Tela2LojistaSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)

        if not user.is_lojista:
            return Response({"error": "Este usuário não é lojista."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Se o perfil já existe, não criamos outro, mas garantimos que a comunidade exista
        if hasattr(user, 'lojista_profile'):
             # Opcional: Se quiser permitir re-tentar caso a comunidade tenha falhado antes, 
             # remova este return e use user.lojista_profile abaixo.
             return Response({"error": "Este usuário já possui um perfil."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        
        # 1. Salva o perfil do lojista
        lojista_profile = serializer.save()

        # 2. CRIAÇÃO SEGURA DA COMUNIDADE
        # Usamos get_or_create para evitar erros se ela já existir
        Community.objects.get_or_create(
            lojista=lojista_profile,
            defaults={
                'nome': f"Comunidade {lojista_profile.company_name}",
                'descricao': f"Bem-vindo à comunidade oficial da {lojista_profile.company_name}! Aqui você encontra novidades e promoções."
            }
        )

        return Response(
            {"message": "Etapa 2 concluída. Perfil e Comunidade criados com sucesso!"},
            status=status.HTTP_201_CREATED
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

class UserListView(generics.ListAPIView):
    """
    Endpoint da API para listar todos os usuários cadastrados.
    Agora também filtra por 'search'.
    """
    # 2. Filtra apenas por lojistas (mais seguro)
    queryset = User.objects.filter(is_lojista=True) 
    serializer_class = UserListSerializer
    
    # --- 3. Adicione estas duas linhas ---
    filter_backends = [SearchFilter]
    # 4. Diga ao Django quais campos procurar
    search_fields = ['full_name', 'lojista_profile__company_category']

class EmpresaListView(generics.ListAPIView):
    """
    Endpoint da API para listar e buscar (search)
    APENAS usuários que são Lojistas/Empresas.
    """
    queryset = User.objects.filter(is_lojista=True).select_related('lojista_profile') # Otimizado
    
    # --- 2. MUDE A LINHA ABAIXO ---
    serializer_class = UserDetailSerializer # <--- Use o serializer de detalhe
    
    permission_classes = [AllowAny] 
    filter_backends = [SearchFilter]
    search_fields = ['full_name', 'lojista_profile__company_category', 'lojista_profile__company_name']
    
    # --- 3. ADICIONE O CONTEXTO (PARA A URL DA IMAGEM) ---
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    

class ClienteListView(generics.ListAPIView):
    """
    Endpoint da API para listar APENAS usuários que são Clientes.
    (Provavelmente só para uso administrativo, então pode ser mais restrito)
    """
    queryset = User.objects.filter(is_cliente=True)
    serializer_class = UserListSerializer # Use um serializer que mostre dados de cliente
    permission_classes = [IsAdminUser]

class GetUserByIdView(generics.RetrieveAPIView):
    """
    Endpoint da API para obter TODOS os detalhes de um usuário (User + Profile) 
    pelo ID.
    """
    
    # 1. Queryset otimizado:
    # .select_related() "pré-busca" os perfis numa única query.
    queryset = User.objects.all().select_related('lojista_profile', 'cliente_profile')
    
    serializer_class = UserDetailSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'user_id'

    # 2. Adicione este método:
    # Isso passa o 'request' para o contexto do serializer.
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

class UserProfileView(APIView):
    """
    Endpoint para o usuário logado ver (GET) ou
    atualizar (PATCH) seu próprio perfil (User + Profile).
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_profile_and_serializer_class(self, user):
        """ Helper para pegar o perfil e o serializer corretos """
        if user.is_lojista:
            try:
                profile = user.lojista_profile
                serializer_class = LojistaProfileDataSerializer
                return profile, serializer_class
            except LojistaProfile.DoesNotExist:
                return None, LojistaProfileDataSerializer
        
        elif user.is_cliente:
            try:
                profile = user.cliente_profile
                serializer_class = ClienteProfileDataSerializer
                return profile, serializer_class
            except ClienteProfile.DoesNotExist:
                return None, ClienteProfileDataSerializer
            
        return None, None # Se não for nem cliente nem lojista

    def get(self, request, *args, **kwargs):
        """
        Retorna os dados do User + os dados do Profile (Lojista ou Cliente)
        """
        user = request.user 
        # Busca o perfil (pode ser None se ainda não foi criado)
        profile_instance, _ = self.get_profile_and_serializer_class(user)
        
        # Sempre serializa os dados do 'User'
        user_serializer = UserDataSerializer(user)
        response_data = {'user': user_serializer.data, 'profile': None}

        # Se o perfil existir, serializa ele
        if profile_instance:
            if user.is_lojista:
                response_data['profile'] = LojistaProfileDataSerializer(profile_instance).data
            elif user.is_cliente:
                response_data['profile'] = ClienteProfileDataSerializer(profile_instance).data

        return Response(response_data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        """
        Atualiza (parcialmente) os dados do User e do Profile.
        O frontend envia todos os dados (nome, interesses, foto) juntos.
        """
        user = request.user
        
        # 1. Atualiza o 'User' (nome de usuário / full_name)
        # 'partial=True' significa que é um PATCH (só muda o que foi enviado)
        user_serializer = UserDataSerializer(user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 2. Atualiza o 'Profile' (foto de perfil ou interesses)
        profile_instance, ProfileSerializer = self.get_profile_and_serializer_class(user)
        
        # Só tenta atualizar se o perfil já existir
        if profile_instance and ProfileSerializer:
            
            profile_serializer = ProfileSerializer(
                profile_instance, data=request.data, partial=True
            )
            
            if profile_serializer.is_valid():
                profile_serializer.save()
            else:
              
                return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
     
        return self.get(request, *args, **kwargs)
   

class ChangePasswordView(APIView):
    """
    Endpoint para o usuário logado (autenticado) alterar sua própria senha.
    Recebe 'password' e 'password_confirm'.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        
        user = request.user
        
        serializer = PasswordChangeSerializer(
            data=request.data, 
            context={'request': request} 
        )

        if serializer.is_valid():
           
            new_password = serializer.validated_data['password']
            
            user.set_password(new_password)
            user.save()
            
            return Response(
                {"message": "Senha alterada com sucesso!"}, 
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
 # views para resetar a senha via email
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "E-mail é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Por segurança, não dizemos se o usuário existe ou não,
            # mas retornamos sucesso para evitar enumeração de usuários.
            return Response({"message": "Se o e-mail existir, um link foi enviado."}, status=status.HTTP_200_OK)

        # 1. Gerar Token e UID
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # 2. Construir o Link para o seu FRONTEND (React)
        # Ajuste a porta se seu React não estiver na 5173
        reset_link = f"http://localhost:5173/redefinir-senha/{uid}/{token}"

        # 3. Enviar E-mail
        send_mail(
            subject="Redefinição de Senha - PROCURAÍ",
            message=f"Olá {user.full_name},\n\nClique no link abaixo para redefinir sua senha:\n\n{reset_link}",
            from_email=settings.EMAIL_HOST_USER, # Configure isso no settings.py
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"message": "Link de redefinição enviado."}, status=status.HTTP_200_OK)


# --- VIEW 2: Efetiva a Troca da Senha ---
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        password = request.data.get('password')

        if not uidb64 or not token or not password:
            return Response({"error": "Dados incompletos"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Decodificar o ID do usuário
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Link inválido"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Verificar se o token é válido
        if default_token_generator.check_token(user, token):
            # 3. Definir a nova senha
            user.set_password(password)
            user.save()
            return Response({"message": "Senha alterada com sucesso!"}, status=status.HTTP_200_OK)
        
        return Response({"error": "Token inválido ou expirado"}, status=status.HTTP_400_BAD_REQUEST)   
    

### viewm pra resetar senha via codigo

class PasswordResetRequestView1(APIView):
    """
    Recebe o e-mail e envia um código de 6 dígitos.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Gera e salva o código
            reset_code = PasswordResetCode.generate_code(user)

            # Envia o E-mail
            send_mail(
                subject="Recuperação de Senha - PROCURAÍ",
                message=f"Olá {user.full_name},\n\nSeu código de recuperação é: {reset_code.code}\n\nEste código expira em 15 minutos.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except User.DoesNotExist:
            # Por segurança, fingimos que deu certo para não revelar se o e-mail existe
            pass

        return Response({"message": "O código foi enviado para o email."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView1(APIView):
    """
    Recebe código e nova senha. Verifica e altera.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmCodeSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            reset_code = serializer.validated_data['reset_code']
            new_password = serializer.validated_data['password']

            # Altera a senha
            user.set_password(new_password)
            user.save()

            # Marca o código como usado
            reset_code.is_used = True
            reset_code.save()

            return Response({"message": "Senha alterada com sucesso!"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetValidateCodeView(APIView):
    """
    Valida se o código recebido pelo usuário é válido.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetValidateCodeSerializer(data=request.data)
        if serializer.is_valid():
            reset_code = serializer.reset_code
            return Response({"message": "Código válido", "user_id": reset_code.user.id})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



