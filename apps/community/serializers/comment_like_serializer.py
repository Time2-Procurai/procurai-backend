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
    autor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comentario
        fields = ['id', 'autor', 'texto', 'data']