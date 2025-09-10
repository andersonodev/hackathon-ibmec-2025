from django.db import models
from django.utils import timezone
from django.conf import settings
import hashlib

class PseudonymSalt(models.Model):
    """
    Salt para geração de pseudônimos anônimos
    Rotacionado mensalmente
    """
    label = models.CharField(
        max_length=20, 
        unique=True,
        help_text="Ex: 2025-01"
    )
    salt = models.CharField(
        max_length=64,
        help_text="Salt criptográfico para pseudônimos"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Salt de Pseudônimo"
        verbose_name_plural = "Salts de Pseudônimos"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Salt {self.label}"


class MoodCheckin(models.Model):
    """
    Check-in diário de humor dos colaboradores
    Armazenado com pseudônimo para garantir anonimato
    """
    created_at = models.DateTimeField(default=timezone.now)
    day = models.DateField(db_index=True)
    score = models.PositiveSmallIntegerField(
        help_text="Humor de 1 a 5"
    )
    comment = models.TextField(blank=True)
    tags = models.JSONField(
        default=list, 
        blank=True,
        help_text="Tags opcionais para categorização"
    )
    pseudo_id = models.CharField(
        max_length=64, 
        db_index=True,
        help_text="Pseudônimo anonimizado do usuário"
    )
    
    class Meta:
        verbose_name = "Check-in de Humor"
        verbose_name_plural = "Check-ins de Humor"
        constraints = [
            models.UniqueConstraint(
                fields=["day", "pseudo_id"], 
                name="unique_daily_checkin"
            )
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Check-in {self.day} - Score: {self.score}"
    
    @classmethod
    def generate_pseudo_id(cls, user_id, day=None):
        """
        Gera pseudônimo para um usuário em uma data específica
        """
        if day is None:
            day = timezone.localdate()
        
        label = day.strftime("%Y-%m")
        try:
            salt_obj = PseudonymSalt.objects.get(label=label)
            salt = salt_obj.salt
        except PseudonymSalt.DoesNotExist:
            # Criar salt se não existir
            salt = cls.create_monthly_salt(label)
        
        pseudo_string = f"{user_id}:{salt}"
        return hashlib.sha256(pseudo_string.encode()).hexdigest()
    
    @classmethod
    def create_monthly_salt(cls, label):
        """
        Cria um novo salt mensal
        """
        import secrets
        salt = secrets.token_hex(32)
        PseudonymSalt.objects.create(label=label, salt=salt)
        return salt
