from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class ConnectaAssignment(models.Model):
    """
    Modelo para atribuições de Conectas - cada colaborador escolhe seu Conecta
    """
    employee = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='connecta_assignment',
        verbose_name="Colaborador"
    )
    connecta = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='assigned_employees',
        verbose_name="Conecta"
    )
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Atribuição")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Atribuição de Conecta"
        verbose_name_plural = "Atribuições de Conectas"
    
    def __str__(self):
        return f"{self.employee.get_full_name()} → {self.connecta.get_full_name()}"
    
    def clean(self):
        # Impede que uma pessoa seja Conecta de si mesma
        if self.employee == self.connecta:
            raise ValidationError("Uma pessoa não pode ser Conecta de si mesma")
        
        # Verifica se o Conecta é um colaborador designado como Conecta
        if not self.connecta.is_connecta and self.connecta.role not in ['admin', 'diretoria']:
            raise ValidationError("Apenas colaboradores designados como Conecta, Admins ou Diretoria podem ser Conectas")


class ConnectaProfile(models.Model):
    """
    Perfil estendido para Conectas com informações adicionais
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='connecta_profile'
    )
    bio = models.TextField(verbose_name="Biografia", help_text="Descrição sobre experiência e especialidades")
    specialties = models.JSONField(
        default=list, 
        verbose_name="Especialidades",
        help_text="Lista de especialidades como ['Bem-estar', 'Liderança', 'Tech Career']"
    )
    is_available = models.BooleanField(
        default=True, 
        verbose_name="Disponível para novos colaboradores"
    )
    max_assignments = models.PositiveIntegerField(
        default=10, 
        verbose_name="Máximo de colaboradores"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Perfil de Conecta"
        verbose_name_plural = "Perfis de Conectas"
    
    def __str__(self):
        return f"Perfil: {self.user.get_full_name()}"
    
    @property
    def current_assignments(self):
        return self.user.assigned_employees.filter(is_active=True).count()
    
    @property
    def is_at_capacity(self):
        return self.current_assignments >= self.max_assignments
