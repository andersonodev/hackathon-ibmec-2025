from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db.models import Avg, Count

class ClimaSnapshot(models.Model):
    """
    Snapshot diário/semanal/mensal dos índices de clima
    Para preservar histórico e performance
    """
    PERIOD_TYPES = [
        ("daily", "Diário"),
        ("weekly", "Semanal"),
        ("monthly", "Mensal"),
        ("quarterly", "Trimestral"),
    ]
    
    date = models.DateField(db_index=True)
    period_type = models.CharField(
        max_length=10,
        choices=PERIOD_TYPES,
        default="daily"
    )
    department = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        help_text="Departamento específico ou geral"
    )
    team = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        help_text="Equipe específica ou geral"
    )
    
    # Métricas de humor
    mood_index = models.FloatField(
        null=True,
        blank=True,
        help_text="Índice de humor 0-100 (null se n<5)"
    )
    mood_count = models.PositiveIntegerField(
        default=0,
        help_text="Número de check-ins considerados"
    )
    mood_collecting = models.BooleanField(
        default=True,
        help_text="Se ainda está coletando dados (n<5)"
    )
    
    # Métricas de voz/relatos
    voice_total = models.PositiveIntegerField(
        default=0,
        help_text="Total de relatos no período"
    )
    voice_positivo = models.PositiveIntegerField(default=0)
    voice_alerta = models.PositiveIntegerField(default=0)
    voice_denuncia = models.PositiveIntegerField(default=0)
    voice_resolvido = models.PositiveIntegerField(default=0)
    voice_escalado = models.PositiveIntegerField(default=0)
    
    # Métricas de tempo
    avg_resolution_time = models.FloatField(
        null=True,
        blank=True,
        help_text="Tempo médio de resolução em horas"
    )
    
    # Temas mais citados
    top_themes = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista de temas mais citados com contagem"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Snapshot de Clima"
        verbose_name_plural = "Snapshots de Clima"
        unique_together = ['date', 'period_type', 'department', 'team']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date', 'period_type']),
            models.Index(fields=['department', 'team']),
        ]
    
    def __str__(self):
        scope = self.team or self.department or "Geral"
        return f"Snapshot {self.get_period_type_display()} - {scope} ({self.date})"
    
    @property
    def collecting_progress(self):
        """
        Retorna progresso da coleta no formato "X/5"
        """
        threshold = settings.K_ANONYMITY_THRESHOLD
        if self.mood_collecting:
            return f"{self.mood_count}/{threshold}"
        return f"{threshold}/{threshold}+"


class TeamBulletin(models.Model):
    """
    Boletins semanais publicados pelos Conectas
    """
    STATUS_CHOICES = [
        ("draft", "Rascunho"),
        ("published", "Publicado"),
        ("archived", "Arquivado"),
    ]
    
    title = models.CharField(
        max_length=200,
        help_text="Título do boletim"
    )
    team = models.CharField(
        max_length=120,
        db_index=True,
        help_text="Equipe/departamento do boletim"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_bulletins",
        help_text="Conecta que criou o boletim"
    )
    
    # Três blocos obrigatórios
    foi_bem = models.TextField(
        help_text="O que foi bem na semana"
    )
    preocupa = models.TextField(
        help_text="O que preocupa/precisa atenção"
    )
    proximos_passos = models.TextField(
        help_text="Próximos passos e ações"
    )
    
    # Metadados
    week_start = models.DateField(
        help_text="Início da semana referente"
    )
    week_end = models.DateField(
        help_text="Fim da semana referente"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="draft"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Métricas opcionais
    mood_summary = models.JSONField(
        default=dict,
        blank=True,
        help_text="Resumo das métricas de humor da semana"
    )
    voice_summary = models.JSONField(
        default=dict,
        blank=True,
        help_text="Resumo dos relatos da semana"
    )
    
    class Meta:
        verbose_name = "Boletim da Equipe"
        verbose_name_plural = "Boletins das Equipes"
        ordering = ['-week_start']
        unique_together = ['team', 'week_start']
        indexes = [
            models.Index(fields=['team', 'status']),
            models.Index(fields=['week_start']),
        ]
    
    def __str__(self):
        return f"Boletim {self.team} - {self.week_start.strftime('%d/%m')} a {self.week_end.strftime('%d/%m')}"
    
    def publish(self):
        """
        Publica o boletim
        """
        self.status = "published"
        self.published_at = timezone.now()
        self.save()


class ExportLog(models.Model):
    """
    Log de exportações de dados
    """
    EXPORT_TYPES = [
        ("clima_csv", "Relatório de Clima (CSV)"),
        ("voice_aggregated", "Relatos Agregados"),
        ("mood_aggregated", "Humor Agregado"),
        ("audit_logs", "Logs de Auditoria"),
        ("bulletin_pdf", "Boletim (PDF)"),
    ]
    
    exported_at = models.DateTimeField(auto_now_add=True)
    export_type = models.CharField(
        max_length=20,
        choices=EXPORT_TYPES
    )
    exported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="Usuário que fez a exportação"
    )
    filters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Filtros aplicados na exportação"
    )
    records_count = models.PositiveIntegerField(
        help_text="Número de registros exportados"
    )
    file_size_bytes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Tamanho do arquivo gerado"
    )
    download_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Quando o link de download expira"
    )
    
    class Meta:
        verbose_name = "Log de Exportação"
        verbose_name_plural = "Logs de Exportações"
        ordering = ['-exported_at']
    
    def __str__(self):
        return f"Export {self.get_export_type_display()} por {self.exported_by.get_full_name()}"


class DashboardWidget(models.Model):
    """
    Configuração de widgets para dashboards personalizados
    """
    WIDGET_TYPES = [
        ("mood_index", "Índice de Humor"),
        ("voice_summary", "Resumo de Relatos"),
        ("resolution_time", "Tempo de Resolução"),
        ("top_themes", "Temas Principais"),
        ("team_comparison", "Comparação de Equipes"),
        ("trend_chart", "Gráfico de Tendência"),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dashboard_widgets"
    )
    widget_type = models.CharField(
        max_length=20,
        choices=WIDGET_TYPES
    )
    title = models.CharField(
        max_length=100,
        help_text="Título do widget"
    )
    position = models.PositiveIntegerField(
        default=0,
        help_text="Posição no dashboard"
    )
    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Configurações específicas do widget"
    )
    active = models.BooleanField(
        default=True,
        help_text="Se o widget está ativo"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Widget do Dashboard"
        verbose_name_plural = "Widgets do Dashboard"
        ordering = ['user', 'position']
        unique_together = ['user', 'widget_type']
    
    def __str__(self):
        return f"{self.user.get_full_name()}: {self.title}"
