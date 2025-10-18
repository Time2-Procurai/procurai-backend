from rest_framework import serializers
from .models import User, ClienteProfile, LojistaProfile


class ClienteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteProfile
        fields = ['interesses']


class LojistaProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LojistaProfile
        # Excluímos 'user' pois ele será criado automaticamente
        exclude = ['user']


# --- Serializers para o Cadastro (juntando tudo) ---

class ClienteCreateSerializer(serializers.ModelSerializer):
    # Incluímos o serializer do perfil aninhado
    cliente_profile = ClienteProfileSerializer(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'password', 'cpf', 'phone', 'cliente_profile']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Separa os dados do perfil dos dados do usuário
        profile_data = validated_data.pop('cliente_profile')

        # Marca este usuário como cliente
        validated_data['is_cliente'] = True

        # Usa o método create_user que AUTOMATICAMENTE CRIPTOGRAFA A SENHA
        user = User.objects.create_user(**validated_data)

        # Cria o perfil do cliente, ligando-o ao usuário recém-criado
        ClienteProfile.objects.create(user=user, **profile_data)

        return user


class LojistaCreateSerializer(serializers.ModelSerializer):
    # Serializer do perfil do lojista aninhado
    lojista_profile = LojistaProfileSerializer(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'password', 'cpf', 'phone', 'lojista_profile']

    def create(self, validated_data):
        profile_data = validated_data.pop('lojista_profile')
        validated_data['is_lojista'] = True

        user = User.objects.create_user(**validated_data)

        LojistaProfile.objects.create(user=user, **profile_data)

        return user