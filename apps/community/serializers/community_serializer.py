from rest_framework import serializers
from apps.community.models import Community
from apps.user.models import User

class CommunitySerializer(serializers.ModelSerializer):
    """
    Serializer básico para comunidade. Vamos usar para listar comunidades.
    """
    numero_de_seguidores = serializers.IntegerField(read_only=True)

    class Meta:
        model = Community
        fields = [
            "id",
            "nome",
            "descricao",
            "criada_em",
        ]

class CommunityDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detalhado para comunidade. Inclui informações adicionais.
    Vamos usar na aba de Comunidade do perfil do lojista.
    """
    numero_de_seguidores = serializers.IntegerField(read_only=True)

    class Meta:
        model = Community
        fields = [
            "id",
            "nome",
            "descricao",
            "numero_de_seguidores",
            "criada_em",
        ]

class CommunityFollowSerializer(serializers.Serializer):
    """
    Serializer para seguir/deixar de seguir uma comunidade.
    Só retorna se um usuário está seguindo ou não a comunidade.
    """
    seguindo = serializers.BooleanField()

class CommunityFollowerSerializer(serializers.ModelSerializer):
    """
    Serializer para listar seguidores de uma comunidade.
    """
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
        ]