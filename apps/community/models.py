from django.db import models
from django.conf import settings 
from apps.user.models import LojistaProfile


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
