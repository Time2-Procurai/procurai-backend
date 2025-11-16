from django.db import models
from django.conf import settings 


from apps.user.models import LojistaProfile 

class Comunidade(models.Model):
    """
    Representa a comunidade de uma loja.
    Baseado no seu classDiagram: "Loja 1 -- 1 Comunidade"
    O seu modelo "Loja" é o LojistaProfile.
    """
    
    lojista_profile = models.OneToOneField(
        LojistaProfile, 
        on_delete=models.CASCADE, 
        related_name='comunidade'
    )
    
    membros = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='comunidades_participantes', 
        blank=True
    )

    def __str__(self):
        return f"Comunidade de {self.lojista_profile.company_name}"


class Publicacao(models.Model):
    comunidade = models.ForeignKey(
        Comunidade,
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
