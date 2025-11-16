from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.user.models import LojistaProfile
from .models import Community

@receiver(post_save, sender=LojistaProfile)
def criar_community_para_lojista(sender, instance, created, **kwargs):
    """"
    Cria uma comunidade automaticamente quando um novo LojistaProfile é criado.
    """
    if created:
        Community.objects.create(
            lojista=instance,
            nome=instance.company_name,
            descricao=f"Comunidade oficial da loja {instance.company_name}."
        )

        