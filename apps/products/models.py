from django.db import models
from django.conf import settings

from apps.notifications.models import Notification

# Create your models here.
class Product(models.Model):

    CATEGORY_CHOICES = [
        ('eletronicos', 'Eletrônicos'),
        ('vestuario', 'Vestuário'),
        ('alimentos_bebidas', 'Alimentos e Bebidas'),
        ('moveis_decoracao', 'Móveis e Decoração'),
        ('livros_midia', 'Livros e Mídia'),
        ('esportes_lazer', 'Esportes e Lazer'),
        ('beleza_cuidados', 'Beleza e Cuidados Pessoais'),
        ('automoveis_veiculos', 'Automóveis e Veículos'),
        ('imoveis', 'Imóveis'),
        ('servicos_profissionais', 'Serviços Profissionais'),
        ('saude_bem_estar', 'Saúde e Bem-estar'),
        ('educacao_cursos', 'Educação e Cursos'),
        ('pets_animais', 'Pets e Animais'),
        ('ferramentas_construcao', 'Ferramentas e Construção'),
        ('arte_artesanato', 'Arte e Artesanato'),
        ('brinquedos_jogos', 'Brinquedos e Jogos'),
        ('joias_acessorios', 'Jóias e Acessórios'),
        ('informatica', 'Informática'),
        ('telefonia', 'Telefonia'),
        ('eletrodomesticos', 'Eletrodomésticos'),
        ('outros', 'Outros'),
    ]


    name = models.CharField(max_length=255, verbose_name='Nome do Produto')
    description = models.TextField(verbose_name='Descrição do Produto')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço do Produto')
    is_negotiable = models.BooleanField(default=False, verbose_name='Preço Negociável')
    category_name = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name='Categoria',
        default='outros'
    )
    product_image = models.ImageField(upload_to='product_images/', verbose_name='Imagem do Produto', null=True, blank=True)
    is_service = models.BooleanField(default=False, verbose_name='É um Serviço')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')
    available = models.BooleanField(default=True, verbose_name='Disponível para Venda')
    is_promotion = models.BooleanField(default=False, verbose_name='Em Promoção')
    old_price = models.DecimalField(
        max_digits=10, decimal_places=2, 
        null=True, blank=True, 
        verbose_name='Preço Antigo (Sem desconto)'
    )
    owner_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Proprietário do Produto',
    )

    def save(self, *args, **kwargs):
        # Detectar se é edição
        if self.pk:
            old = Product.objects.get(pk=self.pk)
            old_is_promo = old.is_promotion
        else:
            old_is_promo = self.is_promotion  # Criando agora → não dispara nada

        super().save(*args, **kwargs)

        # Se antes não era promoção e agora é → criar notificações
        if not old_is_promo and self.is_promotion:
            self.create_promotion_notifications()
    
    def create_promotion_notifications(self):
        # Usuários que favoritaram este produto
        favorited_users = self.favorited_by.values_list('user', flat=True)

        # Criar notificação para cada usuário
        for user_id in favorited_users:
            Notification.objects.create(
                recipient_id=user_id,
                message=f"O produto '{self.name}' entrou em promoção! Agora por R$ {self.price}."
            )
    
class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites', # Permite acessar user.favorites.all()
        verbose_name='Usuário'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='favorited_by', # Permite acessar product.favorited_by.all()
        verbose_name='Produto'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Favoritado em')

    class Meta:
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'
        # Garante que um usuário só pode favoritar o mesmo produto uma vez
        unique_together = ('user', 'product')
        ordering = ['-created_at'] # Ordem padrão: mais recentes primeiro

    def __str__(self):
        return f"{self.user.username} favoritou {self.product.name}"