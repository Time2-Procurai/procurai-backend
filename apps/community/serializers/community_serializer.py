from rest_framework import serializers
from apps.community.models import Community
from apps.user.models import User
from apps.community.models import Publicacao, Comunidade

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

class PublicacaoSerializer(serializers.ModelSerializer):
    autor_email = serializers.ReadOnlyField(source='autor.email') 
    comunidade_id = serializers.ReadOnlyField(source='comunidade.id')  

    class Meta:
        model = Publicacao
        fields = ['id', 'comunidade_id', 'autor', 'autor_email', 'titulo', 'descricao', 'imagem', 'data_publicacao']
        read_only_fields = ['id', 'autor', 'data_publicacao', 'comunidade_id']
