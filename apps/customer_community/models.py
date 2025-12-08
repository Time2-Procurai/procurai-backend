from django.db import models
from django.conf import settings

class ClienteCommunity(models.Model):
    # Opções para o dropdown
    CATEGORIA_CHOICES = [
        ('esportes', 'Esportes'),
        ('bairro', 'Bairro'),
        ('musica', 'Música'),
        ('jogos', 'Jogos'),
        ('educacao', 'Educação'),
        ('outros', 'Outros'),
    ]

    criador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='minhas_comunidades_criadas',
        verbose_name='Criador'
    )

    nome = models.CharField(
        max_length=100,
        verbose_name='Nome da Comunidade'
    )

    categoria = models.CharField(
        max_length=50, 
        choices=CATEGORIA_CHOICES,
        default='outros',
        verbose_name='Categoria da Comunidade'
    )

    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição da Comunidade'
    )
    
    imagem_capa = models.ImageField(
        upload_to='comunidades_clientes/capas/',
        blank=True,
        null=True,
        verbose_name='Foto de Capa'
    )
    
    seguidores = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='comunidades_cliente_seguidas',
        blank=True,
        verbose_name='Membros'
    )

    criada_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )

    class Meta:
        verbose_name = 'Comunidade de Cliente'
        verbose_name_plural = 'Comunidades de Clientes'
        ordering = ['-criada_em']

    def __str__(self):
        return f"{self.nome} ({self.categoria})"