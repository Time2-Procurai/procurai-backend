# Em products/serializers/product.py
from rest_framework import serializers
from ..models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'is_promotion', 'old_price', 'is_negotiable',
            'category_name', 'is_service', 
            'product_image', 
            'available', 'owner_id', 'created_at', 'updated_at'
        ]
        
       
        read_only_fields = (
            'id', 
            'owner_id', 
            'created_at', 
            'updated_at', 
            'available' 
        )