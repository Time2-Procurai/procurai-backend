from rest_framework import serializers
from ..models import Product, Category


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'products_count']
        read_only_fields = ['id', 'slug']
    
    def get_products_count(self, obj):
        return obj.products.filter(available=True).count()


class ProductSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    owner_id = serializers.ReadOnlyField(source='owner.id')
    category_name = serializers.ReadOnlyField(source='category.name')
    category_slug = serializers.ReadOnlyField(source='category.slug')
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'is_negotiable',
            'category',
            'category_name',
            'category_slug',
            'is_service',
            'available',
            'owner',
            'owner_id',
            'created_at',
            'updated_at',
        ]
        
        read_only_fields = ['id', 'owner', 'owner_id', 'created_at', 'updated_at', 
                           'category_name', 'category_slug']


# Serializer para listar produtos (mais leve, sem todos os detalhes)
class ProductListSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    category_name = serializers.ReadOnlyField(source='category.name')
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'is_negotiable', 'category_name', 
                  'is_service', 'owner', 'created_at']