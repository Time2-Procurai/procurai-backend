from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(models.Model):
    # Tipos de notificação (iguais aos que definimos no React)
    TYPES = [
        ('announcement', 'Anúncio Geral'),
        ('favorite_promo', 'Promoção em Favorito'),
        ('new_post', 'Nova Publicação'),
    ]

    # Quem vai receber a notificação
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Destinatário'
    )

    # Quem gerou a notificação 
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generated_notifications',
        verbose_name='Ator (Quem gerou)'
    )

    # Tipo da notificação
    notification_type = models.CharField(max_length=20, choices=TYPES)

    # Título e conteúdo 
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)

    # Campos para ligar a notificação a um objeto específico 
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    is_read = models.BooleanField(default=False, verbose_name='Lida')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notificação para {self.recipient}: {self.notification_type}"