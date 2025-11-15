from django.db import models
from django.conf import settings
from apps.user.models import LojistaProfile

class Community(models.Model):

    # Por enquanto, uma comunidade está vinculada a uma loja necessariamente.
    # No futuro, podemos permitir comunidades independentes.
    lojista = models.OneToOneField(
        LojistaProfile,
        on_delete=models.CASCADE,
        related_name='community',
        verbose_name='Lojista Responsável'
    )

    nome = models.CharField(
        max_length=100,
        verbose_name='Nome da Comunidade'
    )

    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição da Comunidade'
    )

    seguidores = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='comunidades_seguidas',
        blank=True,
        verbose_name='Seguidores da Comunidade'
    )

    criada_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )

    class Meta:
        verbose_name = 'Comunidade'
        verbose_name_plural = 'Comunidades'
    
    def __str__(self):
        return f"Comunidade: {self.nome} - Lojista: {self.lojista.user.company_name}"
    
    @property
    def numero_de_seguidores(self):
        return self.seguidores.count()
