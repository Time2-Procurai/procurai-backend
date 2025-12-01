from django.db import models
from django.conf import settings 
from apps.user.models import LojistaProfile
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import F

class Community(models.Model):

    # Por enquanto, uma comunidade está vinculada a uma loja necessariamente.
    # No futuro, podemos permitir comunidades independentes.
    lojista = models.OneToOneField(
        LojistaProfile,
        on_delete=models.CASCADE,
        related_name='community',
        verbose_name='Lojista Responsável'
    )

    nome = models.CharField(
        max_length=100,
        verbose_name='Nome da Comunidade'
    )

    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição da Comunidade'
    )

    seguidores = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='comunidades_seguidas',
        blank=True,
        verbose_name='Seguidores da Comunidade'
    )

    criada_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )

    class Meta:
        verbose_name = 'Comunidade'
        verbose_name_plural = 'Comunidades'
    
    def __str__(self):
        return f"Comunidade: {self.nome} - Lojista: {self.lojista.user.company_name}"
    
    @property
    def numero_de_seguidores(self):
        return self.seguidores.count()


class Publicacao(models.Model):
    comunidade = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='publicacoes'
    )

    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='publicacoes_criadas'
    )

    titulo = models.CharField(max_length=255, blank=True, null=True)
    descricao = models.TextField()

    imagem = models.ImageField(
        upload_to='publicacoes/imagens/',
        blank=True,
        null=True
    )

    data_publicacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_publicacao']

    def __str__(self):
        return self.titulo or f"Publicação de {self.autor.username}"

class Curtida(models.Model):
    publicacao = models.ForeignKey(
        Publicacao,
        on_delete=models.CASCADE,
        related_name='curtidas'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='curtidas'
    )
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('publicacao', 'usuario')  # evita curtida duplicada

    def __str__(self):
        return f"{self.usuario.email} curtiu {self.publicacao.id}"


class Comentario(models.Model):
    publicacao = models.ForeignKey(
        Publicacao,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comentarios_feitos'
    )
    texto = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentário de {self.autor.email} na publicação {self.publicacao.id}"


class Enquete(models.Model):
    comunidade = models.ForeignKey(
        'Community', 
        on_delete=models.CASCADE,
        related_name='enquetes'
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enquetes_criadas'
    )
    pergunta = models.CharField(max_length=255)
    criada_em = models.DateTimeField(auto_now_add=True)
    
    # Define quando a enquete expira automaticamente
    data_fim = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Data de Encerramento"
    )

    encerrada_manualmente = models.BooleanField(default=False)

    class Meta:
        ordering = ['-criada_em']

    def __str__(self):
        return f"Enquete: {self.pergunta}"

    @property
    def is_ativa(self):
        """
        Verifica se a enquete ainda pode receber votos.
        Retorna False se foi fechada manualmente ou se a data expirou.
        """
        if self.encerrada_manualmente:
            return False
        
        if self.data_fim and timezone.now() > self.data_fim:
            return False
            
        return True

class OpcaoEnquete(models.Model):
    enquete = models.ForeignKey(
        Enquete,
        on_delete=models.CASCADE,
        related_name='opcoes'
    )
    texto = models.CharField(max_length=255)
    
    # NOVO: Contador desnormalizado para performance de leitura (O(1))
    votos_count = models.PositiveIntegerField(default=0)

    class Meta:
        # Ordena pelo mais votado por padrão
        ordering = ['-votos_count'] 

    def __str__(self):
        return f"{self.texto} ({self.votos_count} votos)"
class VotoEnquete(models.Model):
    enquete = models.ForeignKey(
        Enquete,
        on_delete=models.CASCADE,
        related_name='votos'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='votos_enquetes'
    )
    opcao = models.ForeignKey(
        OpcaoEnquete,
        on_delete=models.CASCADE,
        related_name='votos'
    )
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Garante 1 voto por usuário por enquete
        unique_together = ('enquete', 'usuario')

    def clean(self):
        # 1. Valida integridade (Opção pertence à Enquete?)
        if self.opcao.enquete != self.enquete:
            raise ValidationError("A opção selecionada não pertence a esta enquete.")
        
        # 2. Valida se a enquete está ativa (data ou flag manual)
        if not self.enquete.is_ativa:
             raise ValidationError("Esta enquete já está encerrada e não aceita mais votos.")

    def save(self, *args, **kwargs):
        # Verifica se é uma criação (novo voto) para incrementar o contador
        is_new = self.pk is None
        
        # Executa as validações do clean() antes de salvar
        self.clean()
        
        super().save(*args, **kwargs)
        
        if is_new:
            # Se dois usuários votarem no mesmo milissegundo, o banco gerencia a soma.
            self.opcao.votos_count = F('votos_count') + 1
            self.opcao.save(update_fields=['votos_count'])

    def delete(self, *args, **kwargs):
        # Decrementa o contador ao deletar
        self.opcao.votos_count = F('votos_count') - 1
        self.opcao.save(update_fields=['votos_count'])

        super().delete(*args, **kwargs)