from django.db import models
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

class Connecta(models.Model):
    """
    Conecta/Escuta - mediador que recebe e resolve relatos
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="connecta"
    )
    active = models.BooleanField(
        default=False,
        help_text="Se está ativo como Conecta"
    )
    mandate_start = models.DateField(null=True, blank=True)
    mandate_end = models.DateField(null=True, blank=True)
    capacity_max = models.PositiveIntegerField(
        default=12,
        help_text="Número máximo de pessoas que pode atender"
    )
    assigned_count = models.PositiveIntegerField(
        default=0,
        help_text="Número atual de pessoas atribuídas"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Conecta"
        verbose_name_plural = "Conectas"
        ordering = ['user__first_name', 'user__last_name']
    
    def __str__(self):
        return f"Conecta: {self.user.get_full_name() or self.user.username}"
    
    @property
    def is_available(self):
        """
        Verifica se o Conecta tem capacidade para mais pessoas
        """
        return self.active and self.assigned_count < self.capacity_max
    
    def can_accept_assignment(self):
        """
        Verifica se pode aceitar nova atribuição
        """
        return self.is_available


class ConnectaPreference(models.Model):
    """
    Preferência de Conecta escolhida pelo colaborador
    Sistema de seleção individual com janela de 15 dias
    """
    employee = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="connecta_pref"
    )
    preferred_connecta = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="preferred_by",
        help_text="Conecta escolhido pelo colaborador"
    )
    chosen_at = models.DateTimeField(default=timezone.now)
    next_change_at = models.DateTimeField(
        help_text="Próxima data permitida para mudança"
    )
    effective = models.BooleanField(
        default=False,
        help_text="Se a escolha foi homologada (≥2 votos)"
    )
    vote_count = models.PositiveIntegerField(
        default=0,
        help_text="Número de votos que o conecta escolhido tem"
    )
    
    class Meta:
        verbose_name = "Preferência de Conecta"
        verbose_name_plural = "Preferências de Conecta"
        ordering = ['-chosen_at']
    
    def __str__(self):
        status = "Ativa" if self.effective else "Pendente"
        return f"{self.employee.get_full_name()} → {self.preferred_connecta.get_full_name()} ({status})"
    
    def save(self, *args, **kwargs):
        # Calcular próxima data de mudança (15 dias)
        if not self.next_change_at:
            self.next_change_at = self.chosen_at + timedelta(
                days=settings.CONNECTA_CHANGE_INTERVAL_DAYS
            )
        super().save(*args, **kwargs)
    
    def can_change(self):
        """
        Verifica se pode trocar de Conecta (respeitando janela de 15 dias)
        """
        return timezone.now() >= self.next_change_at
    
    @classmethod
    def get_vote_counts(cls):
        """
        Retorna contagem de votos por Conecta
        """
        from django.db.models import Count
        return cls.objects.filter(effective=False).values(
            'preferred_connecta'
        ).annotate(
            votes=Count('id')
        ).order_by('-votes')


class ConnectaHomologation(models.Model):
    """
    Histórico de homologações de Conectas
    Aplicação da regra de corte (≥2 votos)
    """
    homologated_at = models.DateTimeField(auto_now_add=True)
    homologated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Admin que fez a homologação"
    )
    total_preferences = models.PositiveIntegerField(
        help_text="Total de preferências processadas"
    )
    approved_connectas = models.PositiveIntegerField(
        help_text="Conectas aprovados (≥2 votos)"
    )
    rejected_preferences = models.PositiveIntegerField(
        help_text="Preferências rejeitadas (<2 votos)"
    )
    notes = models.TextField(
        blank=True,
        help_text="Observações sobre a homologação"
    )
    
    class Meta:
        verbose_name = "Homologação de Conecta"
        verbose_name_plural = "Homologações de Conectas"
        ordering = ['-homologated_at']
    
    def __str__(self):
        return f"Homologação {self.homologated_at.strftime('%d/%m/%Y')} - {self.approved_connectas} aprovados"
