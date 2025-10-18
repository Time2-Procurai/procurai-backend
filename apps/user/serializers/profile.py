from rest_framework import serializers
from ..models import LojistaProfile

class Tela2LojistaSerializer(serializers.ModelSerializer):
    """
    DTO da Etapa 2. Recebe dados do User e do LojistaProfile,
    atualiza o User e cria o LojistaProfile
    """
    # Campos que serão recebidos e atualizados de User
    full_name = serializers.CharField(required=True, write_only=True)
    cpf = serializers.CharField(required=True, write_only=True)
    phone = serializers.CharField(required=True, allow_blank=True, write_only=True)

    class Meta:
        model = LojistaProfile
        fields = ['full_name', 'cpf', 'phone', 'profile_picture', 'cover_picture',
                  'company_name', 'cnpj', 'company_type', 'company_category',
                  'description', 'operating_hours'
        ]

    # Esse mé_todo será usado futuramente
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        """
        Sobrescrita do mé_todo create para a atualização de User
        e criação de LojistaProfile
        """
        user = self.context['user']
        user_data = {
            'full_name': validated_data.pop('full_name'),
            'cpf': validated_data.pop('cpf'),
            'phone': validated_data.pop('phone'),
        }

        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        lojista_profile = LojistaProfile.objects.create(user=user, **validated_data)

        return lojista_profile

class Tela3LojistaEnderecoSerealizer(serializers.ModelSerializer):
    class Meta:
        model = LojistaProfile
        fields = ['cep', 'street', 'number', 'neighborhood', 'city', 'complement']

