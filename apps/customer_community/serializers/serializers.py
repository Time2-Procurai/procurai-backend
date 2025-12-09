from rest_framework import serializers
from ..models import ClienteCommunity

class ClienteCommunitySerializer(serializers.ModelSerializer):
    criador_nome = serializers.ReadOnlyField(source='criador.username')
    is_criador = serializers.SerializerMethodField()
    criador_foto = serializers.ImageField(source='criador.profile_picture', read_only=True)
    class Meta:
        model = ClienteCommunity
        fields = [
            'id', 
            'nome', 
            'descricao', 
            'categoria', # O campo do dropdown
            'imagem_capa', 
            'criador', 
            'criador_nome',
            'is_criador',
            'criada_em',
            'seguidores',
            'criador_foto'# Retorna lista de IDs. Para contagem, use count no frontend ou campo calculado.
        ]
        read_only_fields = ('id', 'criador', 'criada_em', 'seguidores')

    def get_is_criador(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.criador == request.user
        return False