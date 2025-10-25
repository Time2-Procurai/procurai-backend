from django.db import models
from django.utils.text import slugify
from django.conf import settings

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nome da Categoria')
    slug = models.SlugField(max_length=120, unique=True, blank=True, verbose_name='Slug da Categoria')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Nome do Produto')
    description = models.TextField(verbose_name='Descrição do Produto')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço do Produto')
    is_negotiable = models.BooleanField(default=False, verbose_name='Preço Negociável')
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, related_name='products', 
        verbose_name='Categoria do Produto'
    )
    is_service = models.BooleanField(default=False, verbose_name='É um Serviço')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')
    available = models.BooleanField(default=True, verbose_name='Disponível para Venda')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='products',
        verbose_name='Proprietário do Produto'
    )
    slug = models.SlugField(max_length=255, blank=True, verbose_name='Slug do Produto')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name