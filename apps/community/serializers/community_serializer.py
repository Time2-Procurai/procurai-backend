from rest_framework import serializers
from apps.community.models import Community
from apps.user.models import User
from apps.community.models import Publicacao

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
class CommunityFeedSerializer(serializers.ModelSerializer):
    """
    Serializer para listar comunidades no Feed (seção 'Minhas Comunidades').
    Mapeia os campos da Comunidade para os campos que o Frontend (Card de Empresa) espera.
    """
    # Retornamos o ID do USUÁRIO (Lojista) como 'id', para manter a navegação /perfil/empresa/{id}
    id = serializers.IntegerField(source='lojista.user.id', read_only=True)
    
    # Mapeia o nome da comunidade para 'full_name' (padrão do card de empresa)
    full_name = serializers.CharField(source='nome', read_only=True)
    
    # Pega a foto do perfil do lojista
    profile_picture = serializers.ImageField(source='lojista.profile_picture', read_only=True)
    
    # Pega a categoria da empresa
    company_category = serializers.CharField(source='lojista.company_category', read_only=True)

    # Pega o número de seguidores (propriedade do model)
    numero_de_seguidores = serializers.IntegerField(read_only=True)

    class Meta:
        model = Community
        fields = ['id', 'full_name', 'profile_picture', 'company_category', 'numero_de_seguidores']
        
        
class PublicacaoSerializer(serializers.ModelSerializer):
    autor_email = serializers.ReadOnlyField(source='autor.email')
    comunidade_id = serializers.ReadOnlyField(source='comunidade.id')

    # Campos calculados
    likes = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    total_comentarios = serializers.SerializerMethodField() # <--- O CAMPO QUE FALTAVA
    class Meta:
        model = Publicacao
        fields = [
            'id',
            'comunidade_id', # ID da comunidade Lojista
            'comunidade_cliente', # ID da comunidade Cliente
            'autor',
            'autor_email',
            'titulo',
            'descricao',
            'imagem',
            'data_publicacao',
            'likes',
            'user_has_liked', 
            'total_comentarios',
        ]
        read_only_fields = [
            'id',
            'autor',
            'data_publicacao',
            'comunidade_id',
            'comunidade_cliente',
        ]

    def get_likes(self, obj):
        # conta curtidas com user_has_liked=True
        return obj.curtidas.filter(user_has_liked=True).count()

    def get_user_has_liked(self, obj):
        request = self.context.get("request")

        # Retorna false para usuários não autenticados
        if not request or not request.user.is_authenticated:
            return False

        # Verifica se o usuário logado curtiu
        return obj.curtidas.filter(
            usuario=request.user,
            user_has_liked=True
        ).exists()
        
    def get_total_comentarios(self, obj):
        # Tenta pegar 'comentarios' (seu related_name).
        # Se não achar, tenta 'comentario_set' (padrão do Django).
        # Isso blinda o código contra erro de nome.
        if hasattr(obj, 'comentarios'):
            return obj.comentarios.count()
        elif hasattr(obj, 'comentario_set'):
            return obj.comentario_set.count()
        return 0