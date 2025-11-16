from rest_framework import serializers
from ..models import LojistaProfile,ClienteProfile, User


class ClienteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteProfile
        # 'interesses' está como string no seu React, mas 'Choices' no Django
        # Vamos tratá-lo como texto por enquanto
        fields = ['profile_picture', 'interesses']
        extra_kwargs = {
            'profile_picture': {'required': False},
            'interesses': {'required': False, 'allow_null': True}, 
        }

# 2. Serializer Principal: Lida com o Usuário E o Perfil
class ClienteProfileRegistrationSerializer(serializers.ModelSerializer):
    """
    Este serializer aceita campos "planos" do User E do ClienteProfile
    e os salva nos modelos corretos.
    """
    
    # 1. Adiciona os campos do ClienteProfile aqui, no nível principal
    # 'write_only=True' significa que eles são usados para salvar (upload),
    # mas não são mostrados na resposta.
    profile_picture = serializers.ImageField(write_only=True, required=False, allow_null=True)
    interesses = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = User
        # 2. Lista de TODOS os campos "planos" que o React envia
        fields = (
            'id', 'email', 'full_name', 'username', 
            'cpf', 'phone', 
            'profile_picture', # <-- Campo do Profile
            'interesses'       # <-- Campo do Profile
        )
        read_only_fields = ('id', 'email')
        
        # O 'full_Name' do React não bate com 'full_name' do Django
        # Mas seu React já está enviando 'full_name' no FormData, então está OK.
        # Se você ainda tiver o erro de 'full_name' vazio, 
        # mude 'full_name' para 'full_Name' aqui no 'fields' e no 'update'.

    def update(self, instance, validated_data):
        # 3. Pega os dados do perfil (que agora estão no nível principal)
        profile_picture_file = validated_data.pop('profile_picture', None)
        interesses_json = validated_data.pop('interesses', None)
        
        # 4. Atualiza os campos do 'User' (nome, cpf, etc.)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.username = validated_data.get('username', instance.username)
        instance.cpf = validated_data.get('cpf', instance.cpf)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.save() # Salva o User

        # 5. Atualiza ou Cria o 'ClienteProfile'
        profile, created = ClienteProfile.objects.get_or_create(user=instance)

        # 6. SALVA A IMAGEM
        if profile_picture_file:
            profile.profile_picture = profile_picture_file
        
        # 7. Salva os interesses
        if interesses_json:
            # (Aqui você precisaria converter a string JSON/lista de 'Tecnologia'
            # para o formato 'TECH' do seu model, mas vamos focar na imagem)
            # Exemplo simples (assumindo que o front envia o valor do 'Choice'):
            # profile.interesses = json.loads(interesses_json)[0] 
            pass
            
        profile.save() # Salva o ClienteProfile (com a nova imagem)

        return instance
    
     


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