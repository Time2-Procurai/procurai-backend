from rest_framework import serializers
from ..models import User
from django.contrib.auth import authenticate

from rest_framework import serializers
from django.contrib.auth import authenticate
from ..models import User


class ConfirmDeleteSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError({"detail": "Credenciais inválidas."})
        data['user'] = user
        return data

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name']
        read_only_fields = fields