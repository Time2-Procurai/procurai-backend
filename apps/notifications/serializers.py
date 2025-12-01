from rest_framework import serializers
from .models import Notification 
from django.contrib.humanize.templatetags.humanize import naturaltime

class NotificationSerializer(serializers.ModelSerializer):
    # Dados formatados para o Frontend
    avatar = serializers.ImageField(source='actor.lojista_profile.profile_picture', read_only=True)
    storeName = serializers.CharField(source='actor.full_name', read_only=True) # Ou company_name
    date = serializers.SerializerMethodField()
    
    # Campos extras dependendo do tipo (Product Name, etc)
    productName = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 
            'notification_type', # No front chamamos de 'type'
            'storeName', 
            'avatar', 
            'title', 
            'content', 
            'date',
            'is_read',
            'productName',
            # Campos úteis para navegação
            'object_id', 
            'content_type_id' 
        ]

    def get_date(self, obj):
        # Retorna "Há 2 horas", "Ontem", etc.
        return naturaltime(obj.created_at)

    def get_productName(self, obj):
        # Se o objeto ligado for um Produto, retorna o nome dele
        if obj.content_object and hasattr(obj.content_object, 'name'):
            return obj.content_object.name
        return None
    
    def to_representation(self, instance):
        """
        Mapeia os nomes do backend (notification_type) para o frontend (type).
        """
        data = super().to_representation(instance)
        data['type'] = data.pop('notification_type')
        return data