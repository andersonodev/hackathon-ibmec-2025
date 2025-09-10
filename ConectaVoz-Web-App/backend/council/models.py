from django.db import models
from django.utils import timezone
from django.conf import settings

class CouncilCase(models.Model):
    """
    Caso escalado para o Conselho
    Criado quando Conecta escala um relato crítico
    """
    STATUS_CHOICES = [
        ("aberto", "Aberto"),
        ("andamento", "Em Andamento"),
        ("fechado", "Fechado")
    ]
    
    source_post = models.OneToOneField(
        'voice.VoicePost',
        on_delete=models.CASCADE,
        related_name="council_case"
    )
    created_at = models.DateTimeField(default=timezone.now)
    escalated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="escalated_cases",
        help_text="Conecta que escalou o caso"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_cases",
        help_text="Membro do conselho responsável"
    )
    priority = models.CharField(
        max_length=20,
        choices=[
            ("baixa", "Baixa"),
            ("media", "Média"),
            ("alta", "Alta"),
            ("critica", "Crítica")
        ],
        default="media"
    )
    notes = models.TextField(
        blank=True,
        help_text="Notas e observações do caso"
    )
    actions = models.JSONField(
        default=list,
        help_text="Histórico de ações: [{at, by, action, details}]"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="aberto"
    )
    resolution_summary = models.TextField(
        blank=True,
        help_text="Resumo da resolução final"
    )
    closed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Caso do Conselho"
        verbose_name_plural = "Casos do Conselho"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Caso {self.id} - {self.get_priority_display()} ({self.get_status_display()})"
    
    def add_action(self, user, action, details=""):
        """
        Adiciona uma ação ao histórico do caso
        """
        action_entry = {
            'at': timezone.now().isoformat(),
            'by': user.get_full_name() or user.username,
            'by_id': user.id,
            'action': action,
            'details': details
        }
        self.actions.append(action_entry)
        self.save()
        return action_entry
    
    def close_case(self, user, resolution_summary):
        """
        Fecha o caso com resumo da resolução
        """
        self.status = "fechado"
        self.resolution_summary = resolution_summary
        self.closed_at = timezone.now()
        self.add_action(user, "case_closed", resolution_summary)
        self.save()


class CouncilDecision(models.Model):
    """
    Decisões formais do Conselho
    """
    DECISION_TYPES = [
        ("intervencao", "Intervenção"),
        ("investigacao", "Investigação"),
        ("capacitacao", "Capacitação"),
        ("mudanca_processo", "Mudança de Processo"),
        ("arquivamento", "Arquivamento"),
        ("outros", "Outros")
    ]
    
    case = models.ForeignKey(
        CouncilCase,
        on_delete=models.CASCADE,
        related_name="decisions"
    )
    decision_type = models.CharField(
        max_length=20,
        choices=DECISION_TYPES
    )
    description = models.TextField(
        help_text="Descrição da decisão tomada"
    )
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Responsável pela execução"
    )
    deadline = models.DateField(
        null=True,
        blank=True,
        help_text="Prazo para execução"
    )
    executed = models.BooleanField(
        default=False,
        help_text="Se a decisão foi executada"
    )
    execution_notes = models.TextField(
        blank=True,
        help_text="Notas sobre a execução"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Decisão do Conselho"
        verbose_name_plural = "Decisões do Conselho"
        ordering = ['-created_at']
    
    def __str__(self):
        status = "✓" if self.executed else "○"
        return f"{status} {self.get_decision_type_display()} - Caso {self.case.id}"
    
    def mark_executed(self, notes=""):
        """
        Marca a decisão como executada
        """
        self.executed = True
        self.executed_at = timezone.now()
        self.execution_notes = notes
        self.save()
