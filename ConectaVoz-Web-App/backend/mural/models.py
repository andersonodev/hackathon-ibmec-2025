from django.db import models
from django.utils import timezone
from django.conf import settings

class MuralPost(models.Model):
    """
    Post público no mural da equipe
    Separado dos relatos privados - espaço aberto para comunicação
    """
    STATUS_CHOICES = [
        ("publicado", "Publicado"),
        ("ocultado", "Ocultado")
    ]
    
    created_at = models.DateTimeField(default=timezone.now)
    team = models.CharField(
        max_length=120,
        db_index=True,
        help_text="Equipe/departamento do post"
    )
    text = models.TextField(help_text="Conteúdo do post")
    emoji = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Emoji de humor (1-5), opcional"
    )
    anonymous = models.BooleanField(
        default=False,
        help_text="Se o post é anônimo para a equipe"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Autor do post (sempre armazenado para moderação)"
    )
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default="publicado"
    )
    reactions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Reações por emoji: {'👍': 3, '🎉': 5}"
    )
    moderated_at = models.DateTimeField(null=True, blank=True)
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="moderated_posts",
        help_text="Quem moderou o post"
    )
    moderation_reason = models.TextField(
        blank=True,
        help_text="Motivo da moderação"
    )
    
    class Meta:
        verbose_name = "Post do Mural"
        verbose_name_plural = "Posts do Mural"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['team', 'status', 'created_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        author = "Anônimo" if self.anonymous else (
            self.created_by.get_full_name() if self.created_by else "Usuário removido"
        )
        return f"Post de {author} - {self.created_at.strftime('%d/%m/%Y')}"
    
    def get_author_display(self):
        """
        Retorna o nome do autor considerando anonimato
        """
        if self.anonymous:
            return "Anônimo"
        return self.created_by.get_full_name() if self.created_by else "Usuário removido"
    
    def add_reaction(self, emoji):
        """
        Adiciona uma reação ao post
        """
        if emoji not in self.reactions:
            self.reactions[emoji] = 0
        self.reactions[emoji] += 1
        self.save()
    
    def remove_reaction(self, emoji):
        """
        Remove uma reação do post
        """
        if emoji in self.reactions and self.reactions[emoji] > 0:
            self.reactions[emoji] -= 1
            if self.reactions[emoji] == 0:
                del self.reactions[emoji]
            self.save()
    
    def moderate(self, moderator, reason=""):
        """
        Oculta o post (moderação)
        """
        self.status = "ocultado"
        self.moderated_at = timezone.now()
        self.moderated_by = moderator
        self.moderation_reason = reason
        self.save()


class MuralComment(models.Model):
    """
    Comentários nos posts do mural
    """
    STATUS_CHOICES = [
        ("publicado", "Publicado"),
        ("ocultado", "Ocultado")
    ]
    
    post = models.ForeignKey(
        MuralPost,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    created_at = models.DateTimeField(default=timezone.now)
    text = models.TextField(help_text="Conteúdo do comentário")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Autor do comentário"
    )
    anonymous = models.BooleanField(
        default=False,
        help_text="Se o comentário é anônimo"
    )
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default="publicado"
    )
    moderated_at = models.DateTimeField(null=True, blank=True)
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="moderated_comments"
    )
    
    class Meta:
        verbose_name = "Comentário do Mural"
        verbose_name_plural = "Comentários do Mural"
        ordering = ['created_at']
    
    def __str__(self):
        author = "Anônimo" if self.anonymous else (
            self.author.get_full_name() if self.author else "Usuário removido"
        )
        return f"Comentário de {author}"
    
    def get_author_display(self):
        """
        Retorna o nome do autor considerando anonimato
        Se o post original é anônimo e o comentário é do mesmo autor,
        mantém anonimato
        """
        if self.anonymous or (
            self.post.anonymous and 
            self.author == self.post.created_by
        ):
            return "Anônimo"
        return self.author.get_full_name() if self.author else "Usuário removido"


class MuralReaction(models.Model):
    """
    Reações individuais nos posts (para controle de quem reagiu)
    """
    post = models.ForeignKey(
        MuralPost,
        on_delete=models.CASCADE,
        related_name="user_reactions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    emoji = models.CharField(
        max_length=10,
        help_text="Emoji da reação"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Reação do Mural"
        verbose_name_plural = "Reações do Mural"
        unique_together = ['post', 'user', 'emoji']
    
    def __str__(self):
        return f"{self.user.get_full_name()} {self.emoji} no post {self.post.id}"
