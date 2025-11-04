from rest_framework import serializers
from apps.evaluation.models import Evaluation, EvaluationPhoto

class EvaluationPhotoSerializer(serializers.ModelSerializer):
    # Serializer das fotos
    class Meta:
        model = EvaluationPhoto
        fields = ['id', 'photo', 'uploaded_at']

class EvaluationSerializer(serializers.ModelSerializer):
    """
    Serializer para criação e listagem de avaliações.
    Inclui dados do usuário e do alvo (produto ou loja).
    """

    user_name = serializers.CharField(source='user.full_name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    store_name = serializers.CharField(source='store.company_name', read_only=True)
    photos = EvaluationPhotoSerializer(many=True, read_only=True)

    uploaded_photos = serializers.ListField(
        child=serializers.ImageField(max_length=None, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
        help_text='Fotos enviadas junto com a avaliação.'
    )

    class Meta:
        model = Evaluation
        fields = [
            'id', 'user_name', 'product_name', 'store_name',
            'rating', 'comment', 'created_at', 'photos', 'uploaded_photos'
        ]
    
    def create(self, validated_data):
        """
        Sobrescrita do método create para permitir criação de fotos junto com a avaliação.
        """
        photos_data = validated_data.pop('uploaded_photos', [])
        user = self.context['request'].user

        evaluation = Evaluation.objects.create(user=user, **validated_data)

        for photo in photos_data:
            EvaluationPhoto.objects.create(evaluation=evaluation, photo=photo)

        return evaluation