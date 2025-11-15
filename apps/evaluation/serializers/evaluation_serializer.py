from rest_framework import serializers
from apps.evaluation.models import Evaluation, EvaluationPhoto
from apps.products.models import Product 
from apps.user.models import LojistaProfile, User

class EvaluationPhotoSerializer(serializers.ModelSerializer):
    """ Serializer das fotos (correto, mas vamos usar só a URL) """
    class Meta:
        model = EvaluationPhoto
        # 'photo.url' é mais útil para o frontend
        fields = ['id', 'photo']

# Serializer para mostrar quem escreveu o comentário
class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name'] # Você pode adicionar 'profile_picture' aqui
        read_only = True

class EvaluationSerializer(serializers.ModelSerializer):
    """
    Serializer corrigido para criar e listar avaliações.
    """

    # --- CAMPOS DE LEITURA (Para GET) ---
    # (O que você tinha, mas 'user' é melhor como um objeto)
    user = SimpleUserSerializer(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    store_name = serializers.CharField(source='store.company_name', read_only=True)
    
    # Usa o serializer de fotos para mostrar as URLs
    photos = EvaluationPhotoSerializer(many=True, read_only=True) 

    # --- CAMPOS DE ESCRITA (Para POST) ---
    # O React vai enviar os IDs para estes campos
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True, required=False, allow_null=True
    )
    store = serializers.PrimaryKeyRelatedField(
        queryset=LojistaProfile.objects.all(), write_only=True, required=False, allow_null=True
    )
    
    # Este é o campo que o React usará para enviar os ARQUIVOS
    uploaded_photos = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = Evaluation
        fields = [
            'id', 
            # Campos de Leitura (para GET)
            'user', 'product_name', 'store_name', 'created_at', 'photos',
            
            # Campos de Escrita (para POST)
            'product', 'store', 'uploaded_photos',
            
            # Campos Comuns (Leitura e Escrita)
            'rating', 'comment'
        ]

    def create(self, validated_data):
        """
        Cria a avaliação e salva as fotos.
        """
        # 1. Pega os arquivos de foto
        photos_data = validated_data.pop('uploaded_photos', [])
        
        # 2. Pega o usuário do token (que a view passou no 'context')
        user = self.context['request'].user

        # 3. Cria a avaliação (agora 'validated_data' tem 'product' ou 'store')
        evaluation = Evaluation.objects.create(user=user, **validated_data)

        # 4. Salva cada foto
        for photo in photos_data:
            EvaluationPhoto.objects.create(evaluation=evaluation, photo=photo)

        return evaluation
