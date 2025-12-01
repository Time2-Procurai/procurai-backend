from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.products.models import Product, Favorite
from apps.community.models import Publicacao
from .models import Notification

# 1. Notificar seguidores quando uma Loja faz um NOVO POST
@receiver(post_save, sender=Publicacao)
def notify_new_post(sender, instance, created, **kwargs):
    if created:
        # Achar a comunidade e seus seguidores
        comunidade = instance.comunidade
        seguidores = comunidade.seguidores.all()
        
        # Criar uma notificação para CADA seguidor
        # (Em produção, isso deve ser feito via Celery/Background Task para não travar o request)
        for seguidor in seguidores:
            Notification.objects.create(
                recipient=seguidor,
                actor=instance.autor, # O lojista
                notification_type='new_post',
                title='fez uma nova publicação',
                content=instance.descricao[:100] + '...', # Trecho do post
                content_object=instance # Liga ao Post
            )

# 2. Notificar quando um produto favoritado entra em PROMOÇÃO (ex: preço mudou)
# (Essa lógica requer verificar se o preço baixou, aqui é um exemplo simplificado)
@receiver(post_save, sender=Product)
def notify_price_drop(sender, instance, created, **kwargs):
    if not created and instance.is_negotiable: # Exemplo: se virou negociável ou preço baixou
        # Achar quem favoritou este produto
        # (Assumindo que você criou o model Favorite que discutimos)
        favoritos = Favorite.objects.filter(product=instance)
        
        for fav in favoritos:
            Notification.objects.create(
                recipient=fav.user,
                actor=instance.owner_id, # O lojista dono do produto
                notification_type='favorite_promo',
                title='está com uma promoção no produto que você favoritou',
                content_object=instance # Liga ao Produto
            )