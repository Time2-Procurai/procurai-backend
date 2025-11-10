from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer para a mudança de senha de um usuário logado.
    Valida se as duas senhas são iguais e se a nova senha é forte.
    """
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )

    def validate(self, data):
        # 1. Pega o usuário logado (que vamos passar pelo 'context' da view)
        user = self.context['request'].user
        new_password = data['password']

        # 2. Verifica se a nova senha é igual à antiga
        if user.check_password(new_password):
            raise serializers.ValidationError(
                {'password': 'A nova senha não pode ser igual à senha anterior.'}
            )

        # 3. Verifica se as duas senhas batem
        if new_password != data['password_confirm']:
            raise serializers.ValidationError(
                {"password_confirm": "As senhas não coincidem."}
            )
        
        # 4. Valida a força da nova senha
        try:
            # Passamos o 'user' para a validação (boa prática)
            validate_password(new_password, user=user) 
        except ValidationError as e:
            # Se a senha for muito curta, comum, etc.
            raise serializers.ValidationError({'password': list(e.messages)})
        
        return data