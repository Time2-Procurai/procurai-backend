from rest_framework import serializers
from ..models import ClienteProfile,User
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
        
        token['role'] = role # <-- O React vai ler isso!

        return token
    
class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer que "achata" os dados do User e seu Perfil (Lojista ou Cliente)
    em uma única resposta JSON.
    """

    # --- Campos do ClienteProfile ---
    # Busca 'interesses' em user.cliente_profile.interesses
    # Retorna 'null' se o perfil não existir (ex: se for um Lojista)
    interesses = serializers.CharField(source='cliente_profile.interesses', read_only=True, allow_null=True)

    # --- Campos do LojistaProfile ---
    # Busca 'company_name' em user.lojista_profile.company_name
    company_name = serializers.CharField(source='lojista_profile.company_name', read_only=True, allow_null=True)
    cnpj = serializers.CharField(source='lojista_profile.cnpj', read_only=True, allow_null=True)
    company_type = serializers.CharField(source='lojista_profile.company_type', read_only=True, allow_null=True)
    company_category = serializers.CharField(source='lojista_profile.company_category', read_only=True, allow_null=True)
    description = serializers.CharField(source='lojista_profile.description', read_only=True, allow_null=True)
    operating_hours = serializers.CharField(source='lojista_profile.operating_hours', read_only=True, allow_null=True)
    cep = serializers.CharField(source='lojista_profile.cep', read_only=True, allow_null=True)
    street = serializers.CharField(source='lojista_profile.street', read_only=True, allow_null=True)
    number = serializers.CharField(source='lojista_profile.number', read_only=True, allow_null=True)
    neighborhood = serializers.CharField(source='lojista_profile.neighborhood', read_only=True, allow_null=True)
    city = serializers.CharField(source='lojista_profile.city', read_only=True, allow_null=True)
    complement = serializers.CharField(source='lojista_profile.complement', read_only=True, allow_null=True)
    cover_picture = serializers.ImageField(source='lojista_profile.cover_picture', read_only=True, allow_null=True)

    # --- Campo Conflitante: profile_picture ---
    # Usamos um método para decidir qual foto de perfil enviar
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        # Lista de campos: Todos do User + Todos os campos customizados acima
        fields = [
            'id', 'username', 'email', 'full_name', 'cpf', 'phone', 
            'is_lojista', 'is_cliente',
            
            # Campo customizado (resolvido pelo método abaixo)
            'profile_picture', 

            # Campo do Cliente
            'interesses', 

            # Campos do Lojista
            'company_name', 'cnpj', 'company_type', 'company_category', 
            'description', 'operating_hours', 'cep', 'street', 
            'number', 'neighborhood', 'city', 'complement', 'cover_picture'
        ]

    def get_profile_picture(self, user_instance):
        """
        Este método decide dinamicamente qual URL de foto de perfil retornar
        baseado no tipo de usuário.
        """
        # Precisamos do 'request' para construir a URL completa da imagem
        request = self.context.get('request')
        if not request:
            return None

        try:
            if user_instance.is_lojista and user_instance.lojista_profile.profile_picture:
                return request.build_absolute_uri(user_instance.lojista_profile.profile_picture.url)
            elif user_instance.is_cliente and user_instance.cliente_profile.profile_picture:
                return request.build_absolute_uri(user_instance.cliente_profile.profile_picture.url)
        except AttributeError:
            # Isso acontece se o perfil ainda não foi criado (ex: user_instance.lojista_profile não existe)
            return None
        
        return None # Caso não tenha foto ou perfil