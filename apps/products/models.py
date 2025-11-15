from django.db import models
from django.conf import settings

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
    owner_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Proprietário do Produto',
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name