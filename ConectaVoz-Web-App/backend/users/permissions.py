from rest_framework import permissions
from django.conf import settings

class RoleBasedPermission(permissions.BasePermission):
    """
    Permissão baseada no papel do usuário
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin tem acesso a tudo
        if request.user.is_admin_role:
            return True
        
        # Verificar permissões específicas por view
        view_name = getattr(view, 'basename', '') or view.__class__.__name__
        
        return self.check_role_permission(request.user, view_name, request.method)
    
    def check_role_permission(self, user, view_name, method):
        """
        Verifica permissões específicas por papel
        """
        role = user.role
        
        # Mapeamento de permissões por papel
        permissions_map = {
            'employee': {
                'mood-checkin': ['GET', 'POST'],
                'voice-post': ['GET', 'POST'],
                'mural-post': ['GET', 'POST'],
                'mural-comment': ['GET', 'POST'],
                'connecta-preferences': ['GET', 'POST'],
            },
            'connecta': {
                'mood-checkin': ['GET'],
                'voice-post': ['GET', 'PATCH'],
                'mural-post': ['GET', 'POST', 'PATCH'],
                'mural-comment': ['GET', 'POST', 'PATCH'],
                'connecta-queue': ['GET'],
                'team-bulletins': ['GET', 'POST', 'PATCH'],
            },
            'council': {
                'council-case': ['GET', 'PATCH'],
                'council-decision': ['GET', 'POST', 'PATCH'],
                'clima-report': ['GET'],
            },
            'auditor': {
                'audit-logs': ['GET'],
                'retention-logs': ['GET'],
                'system-events': ['GET'],
                'clima-report': ['GET'],
            }
        }
        
        role_permissions = permissions_map.get(role, {})
        allowed_methods = role_permissions.get(view_name, [])
        
        return method in allowed_methods


class IsOwnerOrConnecta(permissions.BasePermission):
    """
    Permissão para objetos que o usuário criou ou é o Conecta responsável
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin tem acesso a tudo
        if request.user.is_admin_role:
            return True
        
        # Verificar se é o criador
        if hasattr(obj, 'author') and obj.author == request.user:
            return True
        
        # Verificar se é o Conecta responsável
        if hasattr(obj, 'assigned_to') and obj.assigned_to and obj.assigned_to.user == request.user:
            return True
        
        # Verificar se é relato anônimo com pseudônimo
        if hasattr(obj, 'pseudo_id'):
            from mood.models import MoodCheckin
            user_pseudo = MoodCheckin.generate_pseudo_id(request.user.id)
            if obj.pseudo_id == user_pseudo:
                return True
        
        return False


class IsTeamMemberOrModerator(permissions.BasePermission):
    """
    Permissão para membros da equipe ou moderadores
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin tem acesso a tudo
        if request.user.is_admin_role:
            return True
        
        # Verificar se é da mesma equipe
        if hasattr(obj, 'team') and request.user.team == obj.team:
            # Leitura para todos da equipe
            if request.method in permissions.SAFE_METHODS:
                return True
            
            # Moderação para Conectas da equipe
            if request.user.is_connecta or request.user.is_admin_role:
                return True
        
        # Verificar se é o criador
        if hasattr(obj, 'created_by') and obj.created_by == request.user:
            return True
        
        return False


class KAnonymityPermission(permissions.BasePermission):
    """
    Permissão que respeita k-anonimato (n≥5)
    """
    
    def has_permission(self, request, view):
        # Esta permissão é verificada nas views que retornam dados agregados
        # A lógica real de k-anonimato está nas views/serializers
        return request.user and request.user.is_authenticated
    
    @staticmethod
    def check_k_anonymity(queryset, threshold=None):
        """
        Verifica se o queryset atende ao k-anonimato
        """
        if threshold is None:
            threshold = getattr(settings, 'K_ANONYMITY_THRESHOLD', 5)
        
        count = queryset.count()
        collecting = count < threshold
        
        return {
            'collecting': collecting,
            'count': count,
            'threshold': threshold,
            'collecting_progress': f"{count}/{threshold}"
        }


class ConnectaChangePermission(permissions.BasePermission):
    """
    Permissão para mudança de Conecta (respeitando janela de 15 dias)
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Apenas colaboradores podem escolher Conecta
        if not request.user.is_employee:
            return False
        
        # Para POST (criar/alterar preferência), verificar janela
        if request.method == 'POST':
            from connectas.models import ConnectaPreference
            try:
                pref = ConnectaPreference.objects.get(employee=request.user)
                if not pref.can_change():
                    return False
            except ConnectaPreference.DoesNotExist:
                # Primeira escolha, permitir
                pass
        
        return True
