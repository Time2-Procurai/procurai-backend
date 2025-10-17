from django.db import models

class Lojista(models.Model):
    
    TIPO_EMPRESA = [
        ('TECH','Tecnologia'),
        ('FOOD','Alimentação'),
    ]
    
    CATEGORIA_EMPRESA = [
        ('PEQ','Pequena'),
        ('MED','Média'),
        ('GRD','Grande'),
    ]
    
    nome = models.CharField(max_length=100, null=False)
    username = models.CharField(max_length=80, unique=True, null=False)
    senha = models.CharField(max_length=128, null=False)
    email = models.EmailField(unique=True, null=False)
    cpf = models.CharField(max_length=11, unique=True, null=False)
    cnpj = models.CharField(max_length=14, unique=True, null=False)
    tipo = models.CharField(max_length=50, choices=TIPO_EMPRESA, null=False)
    categoria = models.CharField(max_length=50, choices=CATEGORIA_EMPRESA, null=False)
    foto = models.ImageField(upload_to='fotos_lojas/', blank=True, null=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    cep = models.CharField(max_length=8, blank=True, null=True)
    numero = models.IntegerField(blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome

class Cliente(models.Model):
    
    # 1. Corrigido o formato de INTERESSES para uma lista de tuplas (valor_banco, valor_legivel)
    INTERESSES_CHOICES = [
        ('CON', 'Construção'),
        ('SAU', 'Saúde'),
        ('ELE', 'Eletrônicos'),
    ]
    
    nome = models.CharField(max_length=100, null=False)
    username = models.CharField(max_length=80, unique=True, null=False)
    email = models.EmailField(unique=True, null=False)
    cpf = models.CharField(max_length=11, unique=True, null=False)
    foto = models.ImageField(upload_to='fotos_clientes/', blank=True, null=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)
    senha = models.CharField(max_length=128, null=False)  # Adicionado campo de senha
    
    # 2. O campo agora usa a lista de tuplas corrigida
    interesses = models.CharField(max_length=3, choices=INTERESSES_CHOICES, blank=True, null=True)

    # 3. Método __str__ melhorado para ser mais seguro e prático
    def __str__(self):
        return f"{self.nome} ({self.username})"