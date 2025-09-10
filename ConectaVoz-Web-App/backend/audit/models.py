from django.db import models
from django.utils import timezone
from django.conf import settings

class AuditLog(models.Model):
    """
    Log de auditoria para todas as ações importantes no sistema
    100% das mudanças de status, moderação, políticas, papéis, homologações
    """
    ACTION_CATEGORIES = [
        ("auth", "Autenticação"),
        ("voice", "Relatos de Voz"),
        ("mood", "Check-in de Humor"),
        ("connecta", "Conectas"),
        ("council", "Conselho"),
        ("mural", "Mural"),
        ("admin", "Administração"),
        ("system", "Sistema"),
    ]
    
    at = models.DateTimeField(auto_now_add=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Usuário que executou a ação"
    )
    action = models.CharField(
        max_length=64,
        help_text="Tipo de ação realizada"
    )
    category = models.CharField(
        max_length=20,
        choices=ACTION_CATEGORIES,
        help_text="Categoria da ação"
    )
    object_type = models.CharField(
        max_length=64,
        help_text="Tipo do objeto afetado (ex: VoicePost, User)"
    )
    object_id = models.CharField(
        max_length=64,
        help_text="ID do objeto afetado"
    )
    object_repr = models.CharField(
        max_length=200,
        blank=True,
        help_text="Representação textual do objeto"
    )
    meta = models.JSONField(
        default=dict,
        blank=True,
        help_text="Metadados da ação (sem payload sensível)"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP do usuário (quando aplicável)"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent do browser"
    )
    
    class Meta:
        verbose_name = "Log de Auditoria"
        verbose_name_plural = "Logs de Auditoria"
        ordering = ['-at']
        indexes = [
            models.Index(fields=['actor', 'at']),
            models.Index(fields=['category', 'action']),
            models.Index(fields=['object_type', 'object_id']),
            models.Index(fields=['at']),
        ]
    
    def __str__(self):
        actor_name = self.actor.get_full_name() if self.actor else "Sistema"
        return f"{self.at.strftime('%d/%m/%Y %H:%M')} - {actor_name}: {self.action}"
    
    @classmethod
    def log_action(cls, actor, action, category, object_type, object_id, 
                   object_repr="", meta=None, request=None):
        """
        Cria um log de auditoria
        """
        log_entry = cls(
            actor=actor,
            action=action,
            category=category,
            object_type=object_type,
            object_id=str(object_id),
            object_repr=object_repr,
            meta=meta or {}
        )
        
        if request:
            log_entry.ip_address = cls.get_client_ip(request)
            log_entry.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        log_entry.save()
        return log_entry
    
    @staticmethod
    def get_client_ip(request):
        """
        Obtém o IP real do cliente
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DataRetentionLog(models.Model):
    """
    Log de retenção de dados
    Registro de quando dados são removidos por políticas de retenção
    """
    RETENTION_TYPES = [
        ("voice_posts", "Relatos de Voz"),
        ("mood_checkins", "Check-ins de Humor"),
        ("attachments", "Anexos"),
        ("conversations", "Conversas"),
        ("mural_posts", "Posts do Mural"),
        ("audit_logs", "Logs de Auditoria"),
    ]
    
    executed_at = models.DateTimeField(auto_now_add=True)
    retention_type = models.CharField(
        max_length=20,
        choices=RETENTION_TYPES
    )
    policy_name = models.CharField(
        max_length=100,
        help_text="Nome da política de retenção aplicada"
    )
    records_affected = models.PositiveIntegerField(
        help_text="Número de registros removidos"
    )
    date_threshold = models.DateTimeField(
        help_text="Data limite para retenção"
    )
    executed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Usuário que executou (ou sistema automático)"
    )
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detalhes da execução"
    )
    
    class Meta:
        verbose_name = "Log de Retenção de Dados"
        verbose_name_plural = "Logs de Retenção de Dados"
        ordering = ['-executed_at']
    
    def __str__(self):
        return f"Retenção {self.get_retention_type_display()} - {self.records_affected} registros"


class SystemEvent(models.Model):
    """
    Eventos importantes do sistema
    """
    EVENT_TYPES = [
        ("maintenance", "Manutenção"),
        ("backup", "Backup"),
        ("migration", "Migração"),
        ("security", "Segurança"),
        ("performance", "Performance"),
        ("error", "Erro"),
    ]
    
    SEVERITY_LEVELS = [
        ("info", "Informação"),
        ("warning", "Aviso"),
        ("error", "Erro"),
        ("critical", "Crítico"),
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPES
    )
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_LEVELS,
        default="info"
    )
    title = models.CharField(
        max_length=200,
        help_text="Título do evento"
    )
    description = models.TextField(
        help_text="Descrição detalhada do evento"
    )
    affected_components = models.JSONField(
        default=list,
        blank=True,
        help_text="Componentes afetados pelo evento"
    )
    resolved = models.BooleanField(
        default=False,
        help_text="Se o evento foi resolvido"
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(
        blank=True,
        help_text="Notas sobre a resolução"
    )
    
    class Meta:
        verbose_name = "Evento do Sistema"
        verbose_name_plural = "Eventos do Sistema"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', 'severity']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        status = "✓" if self.resolved else "○"
        return f"{status} {self.title} ({self.get_severity_display()})"
