from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Modelo de usuário customizado para o sistema Conecta Voz
    """
    ROLE_CHOICES = [
        ("colaborador", "Colaborador"),
        ("diretoria", "Diretoria"),
        ("admin", "Admin"),
    ]
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default="colaborador",
        verbose_name="Papel"
    )
    department = models.CharField(
        max_length=120, 
        blank=True, 
        null=True,
        verbose_name="Departamento"
    )
    team = models.CharField(
        max_length=120, 
        blank=True, 
        null=True,
        verbose_name="Equipe"
    )
    photo = models.ImageField(
        upload_to='user_photos/',
        blank=True,
        null=True,
        verbose_name="Foto de Perfil",
        help_text="Foto opcional do usuário"
    )
    is_connecta = models.BooleanField(
        default=False,
        verbose_name="É um Conecta",
        help_text="Colaboradores podem ser designados como Conectas"
    )
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        
    def __str__(self):
        conecta_info = " (Conecta)" if self.is_connecta else ""
        return f"{self.get_full_name() or self.username} - {self.get_role_display()}{conecta_info}"
    
    @property
    def is_colaborador(self):
        return self.role == "colaborador"
    
    @property
    def is_diretoria(self):
        return self.role == "diretoria"
    
    @property
    def is_admin_role(self):
        return self.role == "admin"
    
    @property
    def can_be_connecta(self):
        """Apenas colaboradores podem ser Conectas"""
        return self.role == "colaborador"
    
    @property
    def display_name(self):
        """Nome para exibição"""
        return self.get_full_name() or self.username
