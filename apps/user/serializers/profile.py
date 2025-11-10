from rest_framework import serializers
from ..models import LojistaProfile,ClienteProfile, User


class ClienteProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para o perfil do cliente, incluindo dados do usuário associado.
    """
    full_name = serializers.CharField(write_only=True, max_length=255)
    cpf = serializers.CharField(write_only=True, max_length=11)
    phone = serializers.CharField(write_only=True, max_length=20, required=False, allow_blank=True)

    class Meta:
        model = ClienteProfile       
        fields = ['interesses', 'full_name', 'cpf', 'phone']

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
                
        user = validated_data.pop('user')
              
        user_data = {
            'full_name': validated_data.pop('full_name'),
            'cpf': validated_data.pop('cpf'),
            'phone': validated_data.pop('phone'),
        }

       
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        cliente_profile = ClienteProfile.objects.create(user=user, **validated_data)

        return cliente_profile
        
    
    
     


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
                  'company_name', 'cnpj', 'company_category',
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



class UserListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'email','password']


# PÁGINA DE PERFIL (GET e PATCH)

class UserDataSerializer(serializers.ModelSerializer):
    """
    Serializer para LER e ATUALIZAR o 'User'.
    (Isso cuida do "nome de usuário")
    """
    class Meta:
        model = User
        # 'full_name' é o seu "nome de usuário"
        fields = ['id', 'email', 'full_name', 'cpf', 'phone']
        read_only_fields = ['id', 'email']

class LojistaProfileDataSerializer(serializers.ModelSerializer):
    """
    Serializer para LER e ATUALIZAR o 'LojistaProfile'.
    (Isso cuida da "foto de perfil" do Lojista)
    """
    class Meta:
        model = LojistaProfile
        fields = '__all__' # Pega todos os campos (incluindo a foto)
        read_only_fields = ['user']

class ClienteProfileDataSerializer(serializers.ModelSerializer):
    """
    Serializer para LER e ATUALIZAR o 'ClienteProfile'.
    (Isso cuida dos "interesses" E da "foto de perfil" do Cliente)
    """
    class Meta:
        model = ClienteProfile
        fields = '__all__' # Pega todos os campos (incluindo interesses e foto)
        read_only_fields = ['user']