from rest_framework import serializers
from apps.community.models import Curtida, Comentario

class CurtidaSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Curtida
        fields = ['id', 'usuario', 'data','user_has_liked']
        
    def get_user_has_liked(self, obj):
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        return obj.likes_users.filter(id=user.id).exists()

class ComentarioSerializer(serializers.ModelSerializer):
    # Campos calculados para o Frontend
    autor_nome = serializers.SerializerMethodField()
    autor_foto = serializers.SerializerMethodField()
    autor_id = serializers.ReadOnlyField(source='autor.id')

    class Meta:
        model = Comentario
        fields = ['id', 'autor_id', 'autor_nome', 'autor_foto', 'texto', 'data']

    def get_autor_nome(self, obj):
        # Lógica: Se for lojista, manda o nome da empresa. Se for cliente, manda o nome completo.
        if obj.autor.is_lojista and hasattr(obj.autor, 'lojista_profile'):
            return obj.autor.lojista_profile.company_name
        return obj.autor.full_name

    def get_autor_foto(self, obj):
        # Lógica para pegar a foto correta
        request = self.context.get('request')
        foto = None

        if obj.autor.is_lojista and hasattr(obj.autor, 'lojista_profile'):
            foto = obj.autor.lojista_profile.profile_picture
        elif hasattr(obj.autor, 'cliente_profile'):
            foto = obj.autor.cliente_profile.profile_picture
            
        if foto and request:
            return request.build_absolute_uri(foto.url)
        return None