from rest_framework import serializers
from apps.community.models import Publicacao, Comunidade

class PublicacaoSerializer(serializers.ModelSerializer):
    autor_email = serializers.ReadOnlyField(source='autor.email') 
    comunidade_id = serializers.ReadOnlyField(source='comunidade.id')  

    class Meta:
        model = Publicacao
        fields = ['id', 'comunidade_id', 'autor', 'autor_email', 'titulo', 'descricao', 'imagem', 'data_publicacao']
        read_only_fields = ['id', 'autor', 'data_publicacao', 'comunidade_id']
