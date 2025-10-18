from rest_framework import serializers
from ..models import User

class Tela1UserCreationSerializer(serializers.ModelSerializer):
    user_type = serializers.ChoiceField(
        choices=["cliente", "empresa"], write_only=True, label="Tipo de Conta"
    )
    password_confirm = serializers.CharField(
        style={"input_type": "password"}, write_only=True, label="Confirmar Senha"
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'user_type']
        extra_kwargs = {'password': {'write_only': True, 'style': {'input_type': 'password'}}}

    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({"password": "As senhas não são iguais."})
        return data

    def create(self, validated_data):
        user_type = validated_data.pop('user_type')
        if user_type == 'cliente':
            validated_data['is_cliente'] = True
        elif user_type == 'empresa':
            validated_data['is_lojista'] = True

        validated_data['username'] = validated_data['email']

        user = User.objects.create_user(**validated_data)
        return user