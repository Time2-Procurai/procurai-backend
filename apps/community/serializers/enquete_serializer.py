from rest_framework import serializers
from django.db import transaction
from django.db.models import Sum
from apps.community.models import Enquete, OpcaoEnquete, VotoEnquete

class OpcaoEnqueteSerializer(serializers.ModelSerializer):
    votos = serializers.IntegerField(source='votos_count', read_only=True)

    class Meta:
        model = OpcaoEnquete
        fields = ['id', 'texto', 'votos']

class EnqueteSerializer(serializers.ModelSerializer):
    opcoes = OpcaoEnqueteSerializer(many=True, read_only=True)
    total_votos = serializers.SerializerMethodField()
    ativa = serializers.BooleanField(source='is_ativa', read_only=True)
    data_criacao = serializers.DateTimeField(source='criada_em', read_only=True)
    # Adicionado para exibir nome do autor no feed
    autor_nome = serializers.CharField(source='autor.full_name', read_only=True)

    class Meta:
        model = Enquete
        fields = [
            'id',
            'comunidade',
            'autor',
            'autor_nome',
            'pergunta',
            'opcoes',
            'ativa',        
            'data_criacao', 
            'total_votos',  
            'data_fim',
        ]
        
    def get_total_votos(self, obj):
        # Soma otimizada usando o campo pré-calculado 'votos_count'
        return sum(opcao.votos_count for opcao in obj.opcoes.all())

class CriarEnqueteSerializer(serializers.ModelSerializer):
    opcoes = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True,
        required=True,
        min_length=2,
        error_messages={'min_length': 'Informe pelo menos duas opções para a enquete.'}
    )
    data_criacao = serializers.DateTimeField(source='criada_em', read_only=True)
    class Meta:
        model = Enquete
        fields = ['comunidade', 'pergunta', 'opcoes', 'data_fim','data_criacao']
        read_only_fields = ['comunidade']

    def create(self, validated_data):
        opcoes_texto = validated_data.pop('opcoes')
        
        # O 'user' já está dentro de validated_data['autor'] injetado pela View
        
        with transaction.atomic():
            # --- CORREÇÃO AQUI ---
            # Removido 'autor=user'. Usamos apenas **validated_data que já contém autor e comunidade.
            enquete = Enquete.objects.create(**validated_data)

            opcoes_objs = [
                OpcaoEnquete(enquete=enquete, texto=texto) 
                for texto in opcoes_texto
            ]
            OpcaoEnquete.objects.bulk_create(opcoes_objs)

        return enquete
    
class VotoEnqueteSerializer(serializers.ModelSerializer):
    opcao_id = serializers.PrimaryKeyRelatedField(
        queryset=OpcaoEnquete.objects.all(),
        source='opcao',
        write_only=True
    )

    class Meta:
        model = VotoEnquete
        fields = ['opcao_id'] 

    def validate(self, attrs):
        user = self.context['request'].user
        opcao = attrs['opcao']
        enquete = opcao.enquete

        if not enquete.is_ativa:
            raise serializers.ValidationError("Esta enquete já está encerrada.")

        if VotoEnquete.objects.filter(enquete=enquete, usuario=user).exists():
            raise serializers.ValidationError("Você já votou nesta enquete.")

        attrs['usuario'] = user
        attrs['enquete'] = enquete
        return attrs