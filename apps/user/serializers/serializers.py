
from rest_framework import serializers
from ..models import ClienteProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteProfile        
        fields = '__all__'


class MyTokenObtainPairViewSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Chama o método original
        token = super().get_token(user)

        # Adiciona "claims" customizadas ao token
        token['email'] = user.email
        token['user_id'] = user.id

        # Lógica para definir o "role" baseado nos seus campos Booleanos
        role = 'cliente'  # Define 'cliente' como padrão
        if user.is_lojista:
            role = 'lojista'
        
        token['role'] = role

        return token