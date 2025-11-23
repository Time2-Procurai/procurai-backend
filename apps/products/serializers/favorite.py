from rest_framework import serializers
from apps.products.models import Favorite
from apps.products.serializers.product import ProductSerializer # Seu serializer de produto existente

class FavoriteSerializer(serializers.ModelSerializer):
    # Ao listar favoritos, queremos ver os dados do produto, não só o ID
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'product', 'created_at']