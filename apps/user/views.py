from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404
from django.db import transaction
import os

from apps.user.serializers.deleteUser import UserBasicSerializer
from .models import User, LojistaProfile

from .serializers.profile import Tela3LojistaEnderecoSerealizer
from .serializers.profile import Tela2LojistaSerializer
from .serializers.registration import Tela1UserCreationSerializer
from .serializers.deleteUser import ConfirmDeleteSerializer


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

class DeletarContaView(generics.GenericAPIView):
    """
    POST com email+senha para confirmar exclusão.
    Para testes locais permission_classes pode ficar vazio; em produção use IsAuthenticated
    e compare request.user com o usuário autenticado.
    """
    # permission_classes = [IsAuthenticated]
    serializer_class = ConfirmDeleteSerializer

    def _delete_lojista_files(self, lojista):
        for f in (lojista.profile_picture, lojista.cover_picture):
            try:
                if f and hasattr(f, 'path') and os.path.isfile(f.path):
                    os.remove(f.path)
            except Exception:
                pass

    def perform_destroy(self, instance):
        # remover dados relacionados de acordo com o tipo
        if hasattr(instance, 'lojista_profile'):
            loj = instance.lojista_profile
            self._delete_lojista_files(loj)
            loj.delete()
            # aqui: opcionalmente apagar produtos, avaliações, etc.
        if hasattr(instance, 'cliente_profile'):
            instance.cliente_profile.delete()
        # por fim, apagar o usuário
        instance.delete()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Se em produção: garantir que o requester seja o próprio usuário autenticado
        # if request.user != user:
        #     return Response({"detail": "Credenciais não correspondem ao usuário autenticado."},
        #                     status=status.HTTP_403_FORBIDDEN)

        # Regras de negócio específicas
        if getattr(user, 'is_lojista', False):
            # Exemplo: impedir exclusão se houver pedidos pendentes
            # if user_has_pending_orders(user):
            #     return Response({"detail": "Existem pedidos pendentes."}, status=status.HTTP_400_BAD_REQUEST)
            pass

        with transaction.atomic():
            user_data = UserBasicSerializer(user).data
            self.perform_destroy(user)

        return Response({"message": "Conta apagada com sucesso", "user": user_data}, status=status.HTTP_200_OK)
