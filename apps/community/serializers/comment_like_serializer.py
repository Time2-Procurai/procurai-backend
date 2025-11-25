from rest_framework import serializers
from apps.community.models import Curtida, Comentario

class CurtidaSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Curtida
        fields = ['id', 'usuario', 'data']

class ComentarioSerializer(serializers.ModelSerializer):
    autor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comentario
        fields = ['id', 'autor', 'texto', 'data']