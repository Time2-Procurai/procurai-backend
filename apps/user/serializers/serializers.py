
from rest_framework import serializers
from ..models import ClienteProfile

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteProfile        
        fields = '__all__'