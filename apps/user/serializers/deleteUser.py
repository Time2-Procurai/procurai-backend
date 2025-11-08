from rest_framework import serializers
from ..models import User
from django.contrib.auth import authenticate
from rest_framework import serializers
from ..models import User


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name']
        read_only_fields = fields