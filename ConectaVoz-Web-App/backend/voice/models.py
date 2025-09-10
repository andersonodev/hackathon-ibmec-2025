from django.db import models
from django.utils import timezone
from django.conf import settings
from mood.models import MoodCheckin

class VoicePost(models.Model):
    """
    Relato/feedback dos colaboradores para seu Conecta
    """
    SENTIMENT_CHOICES = [
        ("positivo", "Positivo"),
        ("alerta", "Alerta"),
        ("denuncia", "Denúncia")
    ]
    
    VISIBILITY_CHOICES = [
        ("connecta_ident", "Conecta (identificado)"),
        ("connecta_anon", "Conecta (anônimo)")
    ]
    
    STATUS_CHOICES = [
        ("novo", "Novo"),
        ("em_analise", "Em Análise"),
        ("resolvido", "Resolvido"),
        ("escalado", "Escalado")
    ]
    
    created_at = models.DateTimeField(default=timezone.now)
    pseudo_id = models.CharField(
        max_length=64, 
        db_index=True,
        help_text="Pseudônimo anonimizado do autor"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Pode ser nulo para reforço de anonimato"
    )
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="connecta_ident",
        help_text="Nível de privacidade perante o Conecta"
    )
    sentiment = models.CharField(
        max_length=10,
        choices=SENTIMENT_CHOICES,
        help_text="Classificação do relato"
    )
    text = models.TextField(help_text="Conteúdo do relato")
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags para categorização"
    )
    gostaria_retorno = models.BooleanField(
        default=False,
        help_text="Se o autor quer conversar sobre o relato"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="novo"
    )
    assigned_to = models.ForeignKey(
        'connectas.Connecta',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_posts'
    )
    
    class Meta:
        verbose_name = "Relato de Voz"
        verbose_name_plural = "Relatos de Voz"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['sentiment']),
        ]
    
    def __str__(self):
        return f"Relato {self.sentiment} - {self.created_at.strftime('%d/%m/%Y')}"
    
    @property
    def is_anonymous_to_connecta(self):
        return self.visibility == "connecta_anon"
    
    def get_author_display(self):
        """
        Retorna identificação do autor baseada na visibilidade
        """
        if self.is_anonymous_to_connecta:
            return "Anônimo"
        return self.author.get_full_name() if self.author else "Usuário removido"


class VoiceAttachment(models.Model):
    """
    Anexos dos relatos (imagens, documentos)
    """
    post = models.ForeignKey(
        VoicePost,
        on_delete=models.CASCADE,
        related_name="attachments"
    )
    file = models.FileField(
        upload_to="voice_attachments/%Y/%m/",
        help_text="Arquivo anexado ao relato"
    )
    filename = models.CharField(
        max_length=255,
        help_text="Nome original do arquivo"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Anexo de Relato"
        verbose_name_plural = "Anexos de Relatos"
    
    def __str__(self):
        return f"Anexo: {self.filename}"


class Conversation(models.Model):
    """
    Conversa entre autor do relato e Conecta
    Chat cego para manter anonimato quando necessário
    """
    post = models.OneToOneField(
        VoicePost,
        on_delete=models.CASCADE,
        related_name="conversation"
    )
    messages = models.JSONField(
        default=list,
        help_text="Array de mensagens: [{from:'autor|connecta', at:'ISO', text:'...'}]"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Conversa"
        verbose_name_plural = "Conversas"
    
    def __str__(self):
        return f"Conversa - Relato {self.post.id}"
    
    def add_message(self, sender_type, text, sender_user=None):
        """
        Adiciona uma mensagem à conversa
        sender_type: 'autor' ou 'connecta'
        """
        message = {
            'from': sender_type,
            'at': timezone.now().isoformat(),
            'text': text,
        }
        
        # Adicionar identificação se não for anônimo
        if sender_user and not self.post.is_anonymous_to_connecta:
            message['sender_name'] = sender_user.get_full_name()
        
        self.messages.append(message)
        self.save()
        
        return message
