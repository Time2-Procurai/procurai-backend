from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    # Campos com caracteísiticas comuns aos dois tipos de usuário
    full_name = models.CharField(max_length=255, verbose_name='Nome Completo')
    email = models.EmailField(unique=True, verbose_name='E-mail')
    cpf = models.CharField(max_length=11, unique=True, verbose_name='CPF', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefone')
    
    # Campos para identificar se o usuário é Lojista ou Cliente
    is_lojista = models.BooleanField(default=False)
    is_cliente = models.BooleanField(default=False)

    # Definindo que 'email' será usado para login
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username', 'full_name' ,'cpf']

    def __str__(self):
        return self.email

class ClienteProfile(models.Model):
    INTERESSES_CHOICES = [
        ('CON', 'Construção'),
        ('SAU', 'Saúde'),
        ('ELE', 'Eletrônicos'),
    ]
    profile_picture = models.ImageField(upload_to='clientes/profile_pics', null=True, blank=True, verbose_name='Foto de Perfil')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente_profile')

    interesses = models.CharField(
        max_length=3,
        choices=INTERESSES_CHOICES,
        blank=True,
        null=True,
        verbose_name="Interesses"
    )

    def __str__(self):
        return f"Perfil de Cliente de {self.user.username}"

class LojistaProfile(models.Model):
    TIPO_EMPRESA = [('TECH', 'Tecnologia'), ('FOOD', 'Alimentação')]
    # Confirmar a questão da ctegoria
    CATEGORIA_EMPRESA = [('ROUP', 'Roupas e Acessórios'),
        ('ELET', 'Eletrônicos'),
        ('COSM', 'Cosméticos'),
        ('REST', 'Restaurantes'),
        ('Construção', 'Construção'),
        ('Saúde', 'Saúde')
    ]
    
    company_category = models.CharField(max_length=50, choices=CATEGORIA_EMPRESA, verbose_name="Categoria da Empresa")

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lojista_profile')

    profile_picture = models.ImageField(upload_to='lojistas/profile_pics', null=True, blank=True, verbose_name='Foto de Perfil')
    cover_picture = models.ImageField(upload_to='lojistas/cover_pics', null=True, blank=True, verbose_name='Foto de Capa')

    company_name = models.CharField(max_length=255, verbose_name="Nome da Empresa")
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True, verbose_name="CNPJ")
    company_type = models.CharField(max_length=50, choices=TIPO_EMPRESA, verbose_name="Tipo da Empresa")
    
    description = models.TextField(blank=True, null=True, verbose_name="Descrição da Empresa")
    operating_hours = models.CharField(max_length=100, blank=True, null=True, verbose_name="Horário de Funcionamento")

    cep = models.CharField(max_length=9, blank=True, null=True, verbose_name="CEP")
    street = models.CharField(max_length=255, blank=True, null=True, verbose_name="Rua/Avenida")
    number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número")
    neighborhood = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    complement = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")

    def __str__(self):
        return f"Perfil de Lojista de {self.company_name}"