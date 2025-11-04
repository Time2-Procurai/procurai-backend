from django.db import models
from django.conf import settings
from apps.products.models import Product
from apps.user.models import LojistaProfile

class Evaluation(models.Model):

    """
    Avaliação feita por um usuário sobre um produto ou loja.
    A nota é obrigatória. Os comentário e as fotos são opcionais.
    """

    RATING_CHOICES = [
        (1, '1 estrela'),
        (2, '2 estrelas'),
        (3, '3 estrelas'),
        (4, '4 estrelas'),
        (5, '5 estrelas'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='evaluations',
        verbose_name='Usuário que fez a avaliação'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='evaluations',
        null=True,
        blank=True,
        verbose_name='Produto avaliado'
    )

    store = models.ForeignKey(
        LojistaProfile,
        on_delete=models.CASCADE,
        related_name='store_evaluations',
        null=True,
        blank=True,
        verbose_name='Loja avaliada'
    )

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        verbose_name='Nota'
    )

    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Comentário'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data da Avaliação'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )

    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(store__isnull=False, product__isnull=True) |
                    models.Q(store__isnull=True, product__isnull=False)
                ),
                name='evaluation_product_or_store_not_null',
            )
        ]
        ordering = ['-created_at']

    def __str__(self):
        target = self.product.name if self.product else self.store.store_name
        return f"Avaliação de {self.user.username} para {target} - {self.rating} estrelas"

class EvaluationPhoto(models.Model):
    
    evaluation = models.ForeignKey(
        Evaluation,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Avaliação relacionada'
    )

    photo = models.ImageField(
        upload_to='avaliacoes/fotos/',
        verbose_name='Foto da Avaliação'
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Upload'
    )

    def __str__(self):
        return f"Foto da avaliação #{self.evaluation.id}"