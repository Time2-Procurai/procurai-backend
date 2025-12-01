from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from ..models import PasswordResetCode



User = get_user_model()

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
    
    
    # Recupera a nova senha validada

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # A view vai decidir se retorna ou não erro sobre o email existir.
        return value



class PasswordResetConfirmCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=6)
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):

        # 1. Senhas precisam combinar
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                "password_confirm": "As senhas não coincidem."
            })

        # 2. Busca o código mais recente, não usado
        reset_code = PasswordResetCode.objects.filter(
            code=data['code'],
            is_used=False
        ).last()

        if not reset_code or not reset_code.is_valid():
            raise serializers.ValidationError({
                "code": "Código inválido ou expirado."
            })

        # 3. Valida força da nova senha
        try:
            validate_password(data['password'], user=reset_code.user)
        except ValidationError as e:
            raise serializers.ValidationError({
                "password": list(e.messages)
            })

        # 4. Coloca o usuário e o código no data para a view usar
        data['user'] = reset_code.user
        data['reset_code'] = reset_code
        return data

class PasswordResetValidateCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=6)

    def validate_code(self, value):
        try:
            reset_code = PasswordResetCode.objects.get(code=value, is_used=False)
        except PasswordResetCode.DoesNotExist:
            raise serializers.ValidationError("Código inválido ou já usado.")

        if not reset_code.is_valid():
            raise serializers.ValidationError("Código expirado.")

        # Guardamos o reset_code para a view
        self.reset_code = reset_code
        return value
