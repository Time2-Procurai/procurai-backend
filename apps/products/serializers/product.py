# Em products/serializers/product.py
from rest_framework import serializers
from ..models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'is_negotiable',
            'category_name', 'is_service', 
            'product_image', # Assumindo que você adicionou
            'available', 'owner_id', 'created_at', 'updated_at'
        ]
        
        # --- AJUSTE AQUI ---
        # Mova os campos que o servidor define para 'read_only_fields'
        read_only_fields = (
            'id', 
            'owner_id', 
            'created_at', 
            'updated_at', 
            'available' # <-- O MAIS IMPORTANTE
        )