from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.products.models import Product, Favorite
from apps.community.models import Publicacao
from .models import Notification

# 1. Notificar seguidores quando há um NOVO POST (Loja ou Cliente)
@receiver(post_save, sender=Publicacao)
def notify_new_post(sender, instance, created, **kwargs):
    if created:
        seguidores = []

        # --- CASO 1: Post em Comunidade de Lojista ---
        if instance.comunidade:
            seguidores = instance.comunidade.seguidores.all()

        # --- CASO 2: Post em Comunidade de Cliente ---
        elif instance.comunidade_cliente:
            seguidores = instance.comunidade_cliente.seguidores.all()

        # Se não tiver seguidores ou comunidades vinculadas, encerra
        if not seguidores:
            return

        # Criar notificação para cada seguidor
        # (Idealmente usando bulk_create para performance, mas mantive a estrutura original)
        for seguidor in seguidores:
            # Evita notificar o próprio autor do post
            if seguidor == instance.autor:
                continue

            Notification.objects.create(
                recipient=seguidor,
                actor=instance.autor, 
                notification_type='new_post',
                title='fez uma nova publicação',
                content=(instance.descricao[:100] + '...') if instance.descricao else 'Confira o novo post!',
                content_object=instance 
            )

# 2. Notificar quando um produto favoritado entra em PROMOÇÃO
@receiver(post_save, sender=Product)
def notify_price_drop(sender, instance, created, **kwargs):
    if not created and instance.is_negotiable: 
        # Achar quem favoritou este produto
        favoritos = Favorite.objects.filter(product=instance)
        
        for fav in favoritos:
            Notification.objects.create(
                recipient=fav.user,
                actor=instance.owner_id, 
                notification_type='favorite_promo',
                title='está com uma promoção no produto que você favoritou',
                content_object=instance 
            )